from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Collection, CollectionItem
from .serializers import CollectionSerializer, CollectionItemSerializer, CollectionDetailedSerializer
from common.mixins import DetailedSerializerMixin
from drf_spectacular.utils import extend_schema, extend_schema_view

# Create your views here.

@extend_schema_view(
    list=extend_schema(description="컬렉션 목록을 조회합니다.", tags=["Art_collections"]),
    retrieve=extend_schema(description="컬렉션 상세 정보를 조회합니다.", tags=["Art_collections"]),
    create=extend_schema(description="새로운 컬렉션을 생성합니다.", tags=["Art_collections"]),
    update=extend_schema(description="컬렉션 정보를 업데이트합니다.", tags=["Art_collections"]),
    partial_update=extend_schema(description="컬렉션 정보를 부분 업데이트합니다.", tags=["Art_collections"]),
    destroy=extend_schema(description="컬렉션을 삭제합니다.", tags=["Art_collections"])
)
class CollectionViewSet(DetailedSerializerMixin, viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    detailed_serializer_class = CollectionDetailedSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'is_public']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

@extend_schema_view(
    list=extend_schema(description="컬렉션 항목 목록을 조회합니다.", tags=["Art_collections"]),
    retrieve=extend_schema(description="컬렉션 항목 상세 정보를 조회합니다.", tags=["Art_collections"]),
    create=extend_schema(description="새로운 컬렉션 항목을 생성합니다.", tags=["Art_collections"]),
    update=extend_schema(description="컬렉션 항목 정보를 업데이트합니다.", tags=["Art_collections"]),
    partial_update=extend_schema(description="컬렉션 항목 정보를 부분 업데이트합니다.", tags=["Art_collections"]),
    destroy=extend_schema(description="컬렉션 항목을 삭제합니다.", tags=["Art_collections"])
)
class CollectionItemViewSet(viewsets.ModelViewSet):
    queryset = CollectionItem.objects.all()
    serializer_class = CollectionItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['collection', 'artwork']
    ordering_fields = ['order', 'created_at']