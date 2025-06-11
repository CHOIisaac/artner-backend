from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Artwork, ArtworkLike
from .serializers import ArtworkSerializer
from drf_spectacular.utils import extend_schema
from django.db import transaction

# Create your views here.

class ArtworkViewSet(viewsets.GenericViewSet):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer
    
    @extend_schema(
        summary="작품 좋아요 토글",
        description="작품에 좋아요를 추가하거나 취소합니다.",
        tags=["Artworks"]
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, pk=None):
        artwork = self.get_object()
        user = request.user
        
        # 트랜잭션으로 좋아요 처리
        with transaction.atomic():
            # 이미 좋아요한 경우 취소
            try:
                like = ArtworkLike.objects.get(user=user, artwork=artwork)
                like.delete()
                
                # 좋아요 수 감소
                artwork.likes_count = max(0, artwork.likes_count - 1)
                artwork.save(update_fields=['likes_count'])
                
                return Response({'status': 'like removed'}, status=status.HTTP_200_OK)
            
            # 좋아요가 없는 경우 추가
            except ArtworkLike.DoesNotExist:
                ArtworkLike.objects.create(user=user, artwork=artwork)
                
                # 좋아요 수 증가
                artwork.likes_count += 1
                artwork.save(update_fields=['likes_count'])
                
                return Response({'status': 'like added'}, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="작품 좋아요 상태 확인",
        description="작품의 좋아요 상태를 확인합니다.",
        tags=["Artworks"]
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def like_status(self, request, pk=None):
        artwork = self.get_object()
        user = request.user
        
        is_liked = ArtworkLike.objects.filter(user=user, artwork=artwork).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)