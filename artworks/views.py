from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Artwork, ArtworkDetail
from .serializers import ArtworkSerializer, ArtworkDetailSerializer, ArtworkDetailedSerializer
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
    detailed_serializer_class = ArtworkDetailedSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'artist', 'exhibition', 'is_featured']
    search_fields = ['title', 'artist', 'description']
    ordering_fields = ['created_at', 'year', 'title']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detailed_serializer_class
        return self.serializer_class

@extend_schema_view(
    list=extend_schema(description="작품 상세 정보 목록을 조회합니다.", tags=["Artworks"]),
    retrieve=extend_schema(description="작품 상세 정보를 조회합니다.", tags=["Artworks"]),
    create=extend_schema(description="새로운 작품을 생성합니다.", tags=["Artworks"]),
    update=extend_schema(description="작품 상세 정보를 업데이트합니다.", tags=["Artworks"]),
    partial_update=extend_schema(description="작품 상세 정보를 부분 업데이트합니다.", tags=["Artworks"]),
    destroy=extend_schema(description="작품 상세 정보을 삭제합니다.", tags=["Artworks"])
)
class ArtworkDetailViewSet(viewsets.ModelViewSet):
    queryset = ArtworkDetail.objects.all()
    serializer_class = ArtworkDetailSerializer
