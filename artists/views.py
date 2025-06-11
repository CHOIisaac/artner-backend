from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Artist, ArtistLike
from .serializers import ArtistSerializer
from drf_spectacular.utils import extend_schema
from django.db import transaction


# Create your views here.
class ArtistViewSet(viewsets.GenericViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    
    @extend_schema(
        summary="작가 좋아요 토글",
        responses={
            201: {"description": "좋아요 추가됨", "example": {"status": "like added"}},
            200: {"description": "좋아요 제거됨", "example": {"status": "like removed"}}
        },
        tags=["Artists"]
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, pk=None):
        artist = self.get_object()
        user = request.user
        
        # 트랜잭션으로 좋아요 처리
        with transaction.atomic():
            # 이미 좋아요한 경우 취소
            try:
                like = ArtistLike.objects.get(user=user, artist=artist)
                like.delete()
                
                # 좋아요 수 감소
                artist.likes_count = max(0, artist.likes_count - 1)
                artist.save(update_fields=['likes_count'])
                
                return Response({'status': 'like removed'}, status=status.HTTP_200_OK)
            
            # 좋아요가 없는 경우 추가
            except ArtistLike.DoesNotExist:
                ArtistLike.objects.create(user=user, artist=artist)
                
                # 좋아요 수 증가
                artist.likes_count += 1
                artist.save(update_fields=['likes_count'])
                
                return Response({'status': 'like added'}, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="작가 좋아요 상태 확인",
        responses={
            200: {"description": "좋아요 상태", "example": {"is_liked": True}}
        },
        tags=["Artists"]
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def like_status(self, request, pk=None):
        artist = self.get_object()
        user = request.user
        
        is_liked = ArtistLike.objects.filter(user=user, artist=artist).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)
