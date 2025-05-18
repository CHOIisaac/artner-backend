from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Artwork, ArtworkLike
from .serializers import ArtworkSerializer
from common.mixins import DetailedSerializerMixin
from drf_spectacular.utils import extend_schema, extend_schema_view

# Create your views here.

@extend_schema_view(
    list=extend_schema(description="작품 목록을 조회합니다.", tags=["Artworks"]),
    retrieve=extend_schema(description="작품 상세 정보를 조회합니다.", tags=["Artworks"]),
    create=extend_schema(description="새로운 작품을 생성합니다.", tags=["Artworks"]),
    update=extend_schema(description="작품 정보를 업데이트합니다.", tags=["Artworks"]),
    partial_update=extend_schema(description="작품 정보를 부분 업데이트합니다.", tags=["Artworks"]),
    destroy=extend_schema(description="작품을 삭제합니다.", tags=["Artworks"])
)
class ArtworkViewSet(DetailedSerializerMixin, viewsets.ModelViewSet):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'artist', 'description']
    ordering_fields = ['created_at', 'year', 'title']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detailed_serializer_class
        return self.serializer_class
    
    @extend_schema(
        description="작품에 좋아요를 추가하거나 취소합니다.",
        tags=["Artworks"]
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, pk=None):
        artwork = self.get_object()
        user = request.user
        
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
        description="작품의 좋아요 상태를 확인합니다.",
        tags=["Artworks"]
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def like_status(self, request, pk=None):
        artwork = self.get_object()
        user = request.user
        
        is_liked = ArtworkLike.objects.filter(user=user, artwork=artwork).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)