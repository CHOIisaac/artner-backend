from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Artist, ArtistLike
from .serializers import ArtistSerializer
from common.mixins import DetailedSerializerMixin
from drf_spectacular.utils import extend_schema, extend_schema_view

# Create your views here.

@extend_schema_view(
    list=extend_schema(description="작가 목록을 조회합니다.", tags=["Artists"]),
    retrieve=extend_schema(description="작가 상세 정보를 조회합니다.", tags=["Artists"]),
    create=extend_schema(description="새로운 작가를 생성합니다.", tags=["Artists"]),
    update=extend_schema(description="작가 정보를 업데이트합니다.", tags=["Artists"]),
    partial_update=extend_schema(description="작가 정보를 부분 업데이트합니다.", tags=["Artists"]),
    destroy=extend_schema(description="작가를 삭제합니다.", tags=["Artists"])
)
class ArtistViewSet(DetailedSerializerMixin, viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    @extend_schema(
        description="작가에 좋아요를 추가하거나 취소합니다.",
        tags=["Artists"]
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, pk=None):
        artist = self.get_object()
        user = request.user
        
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
        description="작가의 좋아요 상태를 확인합니다.",
        tags=["Artists"]
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def like_status(self, request, pk=None):
        artist = self.get_object()
        user = request.user
        
        is_liked = ArtistLike.objects.filter(user=user, artist=artist).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)
