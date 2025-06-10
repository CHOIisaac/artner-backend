from django.shortcuts import render
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from .models import SaveFolder, SavedItem
from .serializers import DocentHighlightSerializer, SaveFolderSerializer, SavedItemSerializer, \
    SavedItemDetailSerializer, SavedItemCreateSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.db import models, transaction
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Create your views here.
@extend_schema_view(
    list=extend_schema(summary="저장 폴더 목록 조회"),
    retrieve=extend_schema(summary="저장 폴더 상세 조회"),
    create=extend_schema(summary="폴더 생성"),
    update=extend_schema(summary="저장 폴더 전체 수정"),
    partial_update=extend_schema(summary="저장 폴더 부분 수정"),
    destroy=extend_schema(summary="저장 폴더 삭제")
)
class SaveFolderViewSet(viewsets.ModelViewSet):
    """저장 폴더 관리 ViewSet"""
    serializer_class = SaveFolderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        """현재 사용자의 폴더만 조회"""
        return SaveFolder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """폴더 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="폴더 내 저장 항목 목록 조회",
        parameters=[
            OpenApiParameter(name='type', description='항목 유형별 필터링 (all, artist, artwork)', required=False, type=str)
        ],
        responses={200: SavedItemDetailSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """폴더 내 저장된 항목 목록 조회"""
        folder = self.get_object()
        items = folder.items.all()

        # 타입별 필터링
        item_type = request.query_params.get('type')
        if item_type and item_type != 'all':
            items = items.filter(item_type=item_type)

        serializer = SavedItemDetailSerializer(items, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="저장 항목 목록 조회"),
    retrieve=extend_schema(summary="저장 항목 상세 조회"),
    create=extend_schema(summary="새 항목 저장"),
    update=extend_schema(summary="저장 항목 전체 수정"),
    partial_update=extend_schema(summary="저장 항목 부분 수정"),
    destroy=extend_schema(summary="저장 항목 삭제")
)
class SavedItemViewSet(viewsets.ModelViewSet):
    """저장 항목 관리 ViewSet"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['folder', 'item_type']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        """요청 메서드에 따라 적절한 시리얼라이저 반환"""
        if self.action == 'create':
            return SavedItemCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return SavedItemDetailSerializer
        return SavedItemSerializer

    def get_queryset(self):
        """현재 사용자의 저장 항목만 조회"""
        queryset = SavedItem.objects.filter(user=self.request.user)

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

    @extend_schema(
        summary="항목 저장 상태 확인",
        parameters=[
            OpenApiParameter(name='item_type', description='항목 유형 (artist, artwork)', required=True, type=str),
            OpenApiParameter(name='title', description='제목(작가명 또는 작품명)', required=True, type=str)
        ]
    )
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
        saved_items = SavedItem.objects.filter(
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

    @extend_schema(
        summary="항목 저장/삭제 토글",
        request=SavedItemCreateSerializer,
        responses={
            200: {"description": "항목 삭제 성공"},
            201: {"description": "항목 저장 성공"},
            400: {"description": "잘못된 요청"},
            404: {"description": "폴더를 찾을 수 없음"}
        }
    )
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
            folder = SaveFolder.objects.get(id=folder_id, user=request.user)
        except SaveFolder.DoesNotExist:
            return Response(
                {"error": "해당 ID의 폴더가 존재하지 않거나 접근 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 트랜잭션으로 저장/삭제 처리
        with transaction.atomic():
            # 이미 저장된 항목인지 확인
            try:
                item = SavedItem.objects.get(
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

            except SavedItem.DoesNotExist:
                # 저장된 항목이 없으면 새로 저장
                item = SavedItem.objects.create(
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
                        'item': SavedItemDetailSerializer(item).data
                    },
                    status=status.HTTP_201_CREATED
                )


@extend_schema_view(
    list=extend_schema(summary="도슨트 하이라이트 목록 조회", description="도슨트 하이라이트 목록을 조회합니다.", tags=["Docents"]),
    retrieve=extend_schema(summary="도슨트 하이라이트 상세 정보 조회", description="도슨트 하이라이트 상세 정보를 조회합니다.", tags=["Docents"]),
    create=extend_schema(summary="도슨트 하이라이트 생성", description="새로운 도슨트 하이라이트를 생성합니다.", tags=["Docents"]),
    update=extend_schema(summary="도슨트 하이라이트 전체 수정", description="도슨트 하이라이트 정보를 업데이트합니다.", tags=["Docents"]),
    partial_update=extend_schema(summary="도슨트 하이라이트 부분 수정", description="도슨트 하이라이트 정보를 부분 업데이트합니다.", tags=["Docents"]),
    destroy=extend_schema(summary="도슨트 하이라이트 삭제", description="도슨트 하이라이트를 삭제합니다.", tags=["Docents"])
)
class DocentHighlightViewSet(viewsets.ModelViewSet):
    """도슨트 하이라이트 관리를 위한 ViewSet"""
    queryset = DocentHighlight.objects.all()
    serializer_class = DocentHighlightSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """하이라이트 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """사용자별 하이라이트 조회
        - 본인이 생성한 하이라이트
        - 다른 사용자가 생성한 공개 하이라이트
        """
        return DocentHighlight.objects.filter(
            user=self.request.user
        ) | DocentHighlight.objects.filter(
            is_public=True
        )