from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Artwork
from .services import ArtworkService


@extend_schema_view(
    toggle_like=extend_schema(
        summary="작품 좋아요 토글",
        description="작품에 좋아요를 추가하거나 제거합니다.",
        tags=["Likes"]
    ),
    like_status=extend_schema(
        summary="작품 좋아요 상태 확인",
        description="사용자의 작품 좋아요 상태를 확인합니다.",
        tags=["Likes"]
    )
)
class ArtworkViewSet(viewsets.GenericViewSet):
    """
    작품 좋아요 관련 API
    """
    queryset = Artwork.objects.all()  # 라우터 등록에 필요
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.artwork_service = ArtworkService()
    
    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        """좋아요 토글"""
        try:
            result = self.artwork_service.toggle_like(request.user.id, int(pk))
            
            if result['liked']:
                return Response({
                    'status': 'like_added',
                    'likes_count': result['likes_count']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'like_removed',
                    'likes_count': result['likes_count']
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def like_status(self, request, pk=None):
        """좋아요 상태 확인"""
        result = self.artwork_service.get_like_status(request.user.id, int(pk))
        return Response({"is_liked": result['liked']})