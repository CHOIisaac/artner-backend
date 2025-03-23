from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Docent, DocentItem
from .serializers import DocentSerializer, DocentItemSerializer, DocentDetailedSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

# Create your views here.

@extend_schema_view(
    list=extend_schema(description="도슨트 목록을 조회합니다."),
    retrieve=extend_schema(description="도슨트 상세 정보를 조회합니다."),
    create=extend_schema(description="새로운 도슨트를 생성합니다."),
    update=extend_schema(description="도슨트 정보를 업데이트합니다."),
    partial_update=extend_schema(description="도슨트 정보를 부분 업데이트합니다."),
    destroy=extend_schema(description="도슨트를 삭제합니다.")
)
class DocentViewSet(viewsets.ModelViewSet):
    queryset = Docent.objects.all()
    serializer_class = DocentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_public', 'exhibition', 'creator']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'view_count', 'like_count', 'duration']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DocentDetailedSerializer
        return DocentSerializer

@extend_schema_view(
    list=extend_schema(description="도슨트 항목 목록을 조회합니다."),
    retrieve=extend_schema(description="도슨트 항목 상세 정보를 조회합니다.")
)
class DocentItemViewSet(viewsets.ModelViewSet):
    queryset = DocentItem.objects.all()
    serializer_class = DocentItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['docent', 'artwork']
    ordering_fields = ['order', 'duration']
