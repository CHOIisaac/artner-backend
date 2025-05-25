from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from .models import SaveFolder, SaveItem
from .serializers import (
    SaveFolderSerializer, 
    SaveItemSerializer, 
    SaveItemDetailSerializer,
    CreateSaveItemSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="저장 폴더 목록 조회",
        tags=["Saves"]
    ),
    retrieve=extend_schema(
        summary="저장 폴더 상세 조회",
        tags=["Saves"]
    ),
    update=extend_schema(
        summary="저장 폴더 전체 수정",
        tags=["Saves"]
    ),
    partial_update=extend_schema(
        summary="저장 폴더 부분 수정",
        tags=["Saves"]
    ),
    destroy=extend_schema(
        summary="저장 폴더 삭제",
        tags=["Saves"]
    )
)
class SaveFolderViewSet(viewsets.ModelViewSet):
    """사용자의 저장 폴더 관리를 위한 ViewSet"""
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
            OpenApiParameter(name='type', description='항목 유형별 필터링 (artist, artwork, exhibition)', required=False, type=str)
        ],
        responses={200: SaveItemDetailSerializer(many=True)},
        tags=["Saves"]
    )
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """폴더 내 저장된 항목 목록 조회"""
        folder = self.get_object()
        items = SaveItem.objects.filter(folder=folder)
        
        # 필터링 옵션 (항목 유형별)
        item_type = request.query_params.get('type')
        if item_type:
            items = items.filter(item_type=item_type)
        
        serializer = SaveItemDetailSerializer(items, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="저장 항목 목록 조회",
        tags=["Saves"]
    ),
    retrieve=extend_schema(
        summary="저장 항목 상세 조회",
        tags=["Saves"]
    ),
    create=extend_schema(
        summary="새 항목 저장",
        tags=["Saves"]
    ),
    destroy=extend_schema(
        summary="저장 항목 삭제",
        tags=["Saves"]
    )
)
class SaveItemViewSet(viewsets.ModelViewSet):
    """저장 항목 관리를 위한 ViewSet"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['folder', 'item_type']
    ordering_fields = ['created_at']
    http_method_names = ['get', 'post', 'delete']  # PUT, PATCH 메서드 비활성화
    
    def get_serializer_class(self):
        """요청 메서드에 따라 적절한 시리얼라이저 반환"""
        if self.action == 'create':
            return CreateSaveItemSerializer
        elif self.action in ['retrieve', 'list']:
            return SaveItemDetailSerializer
        return SaveItemSerializer
    
    def get_queryset(self):
        """현재 사용자의 저장 항목만 조회"""
        return SaveItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """항목 저장 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        summary="항목 저장 상태 확인",
        parameters=[
            OpenApiParameter(name='item_type', description='항목 유형 (artist, artwork, exhibition)', required=True, type=str),
            OpenApiParameter(name='item_id', description='항목 ID', required=True, type=int)
        ],
        tags=["Saves"]
    )
    @action(detail=False, methods=['get'])
    def status(self, request):
        """항목 저장 상태 확인"""
        item_type = request.query_params.get('item_type')
        item_id = request.query_params.get('item_id')
        
        if not item_type or not item_id:
            return Response(
                {"error": "item_type과 item_id 쿼리 파라미터가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 해당 항목이 저장된 폴더 목록 확인
        saved_items = SaveItem.objects.filter(
            user=request.user,
            item_type=item_type,
            item_id=item_id
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
        request={"application/json": {"example": {"folder_id": 1, "item_type": "artist", "item_id": 1, "notes": "메모 내용(선택사항)"}}},
        tags=["Saves"]
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """항목 저장/삭제 토글"""
        folder_id = request.data.get('folder_id')
        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')
        notes = request.data.get('notes', '')
        
        # 필수 파라미터 확인
        if not folder_id or not item_type or not item_id:
            return Response(
                {"error": "folder_id, item_type, item_id가 필요합니다."}, 
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
        
        # 항목 유형 유효성 검사
        if item_type not in [choice[0] for choice in SaveItem.ITEM_TYPES]:
            return Response(
                {"error": f"유효하지 않은 항목 유형입니다. 가능한 값: {', '.join([choice[0] for choice in SaveItem.ITEM_TYPES])}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 항목 존재 여부 확인
        if item_type == 'artist':
            from artists.models import Artist
            if not Artist.objects.filter(id=item_id).exists():
                return Response(
                    {"error": "해당 ID의 작가가 존재하지 않습니다."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        elif item_type == 'artwork':
            from artworks.models import Artwork
            if not Artwork.objects.filter(id=item_id).exists():
                return Response(
                    {"error": "해당 ID의 작품이 존재하지 않습니다."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        elif item_type == 'exhibition':
            from exhibitions.models import Exhibition
            if not Exhibition.objects.filter(id=item_id).exists():
                return Response(
                    {"error": "해당 ID의 전시회가 존재하지 않습니다."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # 이미 저장된 항목인지 확인
        try:
            save_item = SaveItem.objects.get(
                user=request.user,
                folder=folder,
                item_type=item_type,
                item_id=item_id
            )
            
            # 저장된 항목이 있으면 삭제
            save_item.delete()
            return Response(
                {'status': 'unsaved', 'message': '항목이 저장 목록에서 삭제되었습니다.'}, 
                status=status.HTTP_200_OK
            )
            
        except SaveItem.DoesNotExist:
            # 저장된 항목이 없으면 새로 저장
            save_item = SaveItem.objects.create(
                user=request.user,
                folder=folder,
                item_type=item_type,
                item_id=item_id,
                notes=notes
            )
            
            return Response(
                {
                    'status': 'saved', 
                    'message': '항목이 저장되었습니다.',
                    'save_item': {
                        'id': save_item.id,
                        'folder': {'id': folder.id, 'name': folder.name},
                        'item_type': save_item.item_type,
                        'item_id': save_item.item_id,
                        'notes': save_item.notes
                    }
                }, 
                status=status.HTTP_201_CREATED
            )
