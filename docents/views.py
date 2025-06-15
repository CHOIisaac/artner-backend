from django.shortcuts import render
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.db import models, transaction
from rest_framework.response import Response

from docents.models import Folder, FolderItem, DocentScript
from docents.serializers import (
    FolderSerializer, FolderItemDetailSerializer, 
    FolderItemCreateSerializer, FolderItemSerializer,
    DocentScriptSerializer, DocentScriptCreateSerializer
)
from docents.services import DocentService


# Create your views here.
@extend_schema_view(
    list=extend_schema(
        summary="폴더 목록 조회",
        tags=["Collections"]
    ),
    create=extend_schema(
        summary="폴더 생성",
        tags=["Collections"]
    ),
    partial_update=extend_schema(
        summary="폴더 부분 수정",
        tags=["Collections"]
    ),
    destroy=extend_schema(
        summary="폴더 삭제",
        tags=["Collections"]
    ),
)
class FolderViewSet(viewsets.ModelViewSet):
    """저장 폴더 관리 ViewSet"""
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """현재 사용자의 폴더만 조회"""
        return Folder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """폴더 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="저장된 항목 목록 조회",
        tags=["Collections"]
    ),
    create=extend_schema(
        summary="새 항목 저장",
        tags=["Collections"]
    ),
    partial_update=extend_schema(
        summary="저장된 항목 부분 수정",
        tags=["Collections"]
    ),
    destroy=extend_schema(
        summary="저장된 항목 삭제",
        tags=["Collections"]
    ),
    status=extend_schema(
        summary="저장 상태 확인",
        parameters=[
            OpenApiParameter(name='item_type', description='항목 유형 (artist, artwork)', required=True, type=str),
            OpenApiParameter(name='title', description='제목(작가명 또는 작품명)', required=True, type=str)
        ],
        tags=["Collections"]
    ),
    toggle=extend_schema(
        summary="항목 저장/삭제 토글",
        request=FolderItemCreateSerializer,
        responses={
            200: {"description": "항목 삭제 성공"},
            201: {"description": "항목 저장 성공"},
            400: {"description": "잘못된 요청"},
            404: {"description": "폴더를 찾을 수 없음"}
        },
        tags=["Collections"]
    )
)
class FolderItemViewSet(viewsets.ModelViewSet):
    """저장 항목 관리 ViewSet"""
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['folder', 'item_type']
    ordering_fields = ['created_at', 'title']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """요청 메서드에 따라 적절한 시리얼라이저 반환"""
        if self.action == 'create':
            return FolderItemCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return FolderItemDetailSerializer
        return FolderItemSerializer

    def get_queryset(self):
        """현재 사용자의 저장 항목만 조회"""
        queryset = FolderItem.objects.filter(user=self.request.user)

        # 타입별 필터링 (all, artist, artwork)
        item_type = self.request.query_params.get('type')
        if item_type and item_type != 'all':
            queryset = queryset.filter(item_type=item_type)

        # 폴더별 필터링
        folder_id = self.request.query_params.get('folder')
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)

        return queryset

    def perform_create(self, serializer):
        """항목 저장 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """항목 저장 상태 확인"""
        item_type = request.query_params.get('item_type')
        title = request.query_params.get('title')

        if not item_type or not title:
            return Response(
                {"error": "item_type과 title 쿼리 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 해당 항목이 저장된 폴더 목록 확인
        saved_items = FolderItem.objects.filter(
            user=request.user,
            item_type=item_type,
            title=title
        )

        folders = []
        for item in saved_items:
            folders.append({
                'id': item.folder.id,
                'name': item.folder.name
            })

        return Response({
            'is_saved': len(folders) > 0,
            'folders': folders
        })

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """항목 저장/삭제 토글"""
        folder_id = request.data.get('folder_id')
        item_type = request.data.get('item_type')
        title = request.data.get('title')

        # 추가 데이터
        life_period = request.data.get('life_period', '')
        artist_name = request.data.get('artist_name', '')
        notes = request.data.get('notes', '')
        thumbnail = request.data.get('thumbnail')

        # 필수 파라미터 확인
        if not all([folder_id, item_type, title]):
            return Response(
                {"error": "folder_id, item_type, title이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 폴더 확인
        try:
            folder = Folder.objects.get(id=folder_id, user=request.user)
        except Folder.DoesNotExist:
            return Response(
                {"error": "해당 ID의 폴더가 존재하지 않거나 접근 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 트랜잭션으로 저장/삭제 처리
        with transaction.atomic():
            # 이미 저장된 항목인지 확인
            try:
                item = FolderItem.objects.get(
                    user=request.user,
                    folder=folder,
                    item_type=item_type,
                    title=title
                )

                # 저장된 항목이 있으면 삭제
                item.delete()
                return Response(
                    {'status': 'unsaved', 'message': '항목이 저장 목록에서 삭제되었습니다.'},
                    status=status.HTTP_200_OK
                )

            except FolderItem.DoesNotExist:
                # 저장된 항목이 없으면 새로 저장
                item = FolderItem.objects.create(
                    user=request.user,
                    folder=folder,
                    item_type=item_type,
                    title=title,
                    life_period=life_period if item_type == 'artist' else '',
                    artist_name=artist_name if item_type == 'artwork' else '',
                    notes=notes
                )

                # 썸네일 처리
                if thumbnail:
                    item.thumbnail = thumbnail
                    item.save()

                return Response(
                    {
                        'status': 'saved',
                        'message': '항목이 저장되었습니다.',
                        'item': FolderItemDetailSerializer(item).data
                    },
                    status=status.HTTP_201_CREATED
                )


@extend_schema_view(
    list=extend_schema(
        summary="도슨트 스크립트 목록 조회",
        tags=["Docents"]
    ),
    create=extend_schema(
        summary="도슨트 스크립트 생성",
        tags=["Docents"]
    ),
    destroy=extend_schema(
        summary="도슨트 스크립트 삭제",
        tags=["Docents"]
    )
)
class DocentScriptViewSet(viewsets.ModelViewSet):
    """도슨트 스크립트 관리 ViewSet"""
    queryset = DocentScript.objects.all()
    serializer_class = DocentScriptSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['item_type', 'item_name']
    search_fields = ['item_name', 'item_info', 'llm_response']
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocentScriptCreateSerializer
        return DocentScriptSerializer
    
    def create(self, request, *args, **kwargs):
        """도슨트 스크립트 생성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 도슨트 서비스를 통해 스크립트 생성
            docent_service = DocentService()
            docent = docent_service.create_docent(**serializer.validated_data)
            
            # 생성된 스크립트 반환
            response_serializer = DocentScriptSerializer(docent)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['POST'])
async def generate_realtime_docent(request):
    """실시간 도슨트 생성 API"""
    try:
        artist_name = request.data.get('artist_name')
        if not artist_name:
            return Response(
                {'error': '아티스트 이름이 필요합니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        docent_service = DocentService()
        result = await docent_service.generate_realtime_docent(artist_name)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )