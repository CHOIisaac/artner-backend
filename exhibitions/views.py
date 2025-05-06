from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Exhibition
from .serializers import ExhibitionSerializer
from common.mixins import DetailedSerializerMixin
from drf_spectacular.utils import extend_schema, extend_schema_view

# Create your views here.

@extend_schema_view(
    list=extend_schema(description="전시회 목록을 조회합니다.", tags=["Exhibitions"]),
    retrieve=extend_schema(description="전시회 상세 정보를 조회합니다.", tags=["Exhibitions"]),
    create=extend_schema(description="새로운 전시회를 생성합니다.", tags=["Exhibitions"]),
    update=extend_schema(description="전시회 정보를 업데이트합니다.", tags=["Exhibitions"]),
    partial_update=extend_schema(description="전시회 정보를 부분 업데이트합니다.", tags=["Exhibitions"]),
    destroy=extend_schema(description="전시회를 삭제합니다.", tags=["Exhibitions"])
)
class ExhibitionViewSet(DetailedSerializerMixin, viewsets.ModelViewSet):
    queryset = Exhibition.objects.all()
    serializer_class = ExhibitionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'venue']
    search_fields = ['title', 'description', 'artists']
    ordering_fields = ['start_date', 'end_date', 'created_at']

# @extend_schema_view(
#     list=extend_schema(description="전시회 이미지 목록을 조회합니다.", tags=["Exhibitions"]),
#     retrieve=extend_schema(description="전시회 이미지 상세 정보를 조회합니다.", tags=["Exhibitions"]),
#     create=extend_schema(description="새로운 전시회 이미지를 생성합니다.", tags=["Exhibitions"]),
#     update=extend_schema(description="전시회 이미지 정보를 업데이트합니다.", tags=["Exhibitions"]),
#     partial_update=extend_schema(description="전시회 이미지 정보를 부분 업데이트합니다.", tags=["Exhibitions"]),
#     destroy=extend_schema(description="전시회 이미지를 삭제합니다.", tags=["Exhibitions"])
# )
# class ExhibitionImageViewSet(viewsets.ModelViewSet):
#     queryset = ExhibitionImage.objects.all()
#     serializer_class = ExhibitionImageSerializer
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['exhibition']
#     ordering_fields = ['order']
