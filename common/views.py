from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tag, Review
from .serializers import TagSerializer, ReviewSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

# Create your views here.

@extend_schema_view(
    list=extend_schema(description="태그 목록을 조회합니다.", tags=["Common"]),
    retrieve=extend_schema(description="태그 상세 정보를 조회합니다.", tags=["Common"]),
    create=extend_schema(description="새로운 태그를 생성합니다.", tags=["Common"]),
    update=extend_schema(description="태그 정보를 업데이트합니다.", tags=["Common"]),
    partial_update=extend_schema(description="태그 정보를 부분 업데이트합니다.", tags=["Common"]),
    destroy=extend_schema(description="태그를 삭제합니다.", tags=["Common"])
)
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

@extend_schema_view(
    list=extend_schema(description="리뷰 목록을 조회합니다.", tags=["Common"]),
    retrieve=extend_schema(description="리뷰 상세 정보를 조회합니다.", tags=["Common"]),
    create=extend_schema(description="새로운 리뷰를 생성합니다.", tags=["Common"]),
    update=extend_schema(description="리뷰 정보를 업데이트합니다.", tags=["Common"]),
    partial_update=extend_schema(description="리뷰 정보를 부분 업데이트합니다.", tags=["Common"]),
    destroy=extend_schema(description="리뷰를 삭제합니다.", tags=["Common"])
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'content_type', 'object_id', 'rating']
    ordering_fields = ['created_at', 'rating']
