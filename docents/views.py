from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Docent, DocentItem, DocentHighlight
from .serializers import DocentSerializer, DocentItemSerializer, DocentDetailedSerializer, DocentHighlightSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db import models

# Create your views here.


@extend_schema_view(
    list=extend_schema(description="도슨트 목록을 조회합니다.", tags=["Docents"]),
    retrieve=extend_schema(description="도슨트 상세 정보를 조회합니다.", tags=["Docents"]),
    create=extend_schema(description="새로운 도슨트를 생성합니다.", tags=["Docents"]),
    update=extend_schema(description="도슨트 정보를 업데이트합니다.", tags=["Docents"]),
    partial_update=extend_schema(description="도슨트 정보를 부분 업데이트합니다.", tags=["Docents"]),
    destroy=extend_schema(description="도슨트를 삭제합니다.", tags=["Docents"])
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
    list=extend_schema(description="도슨트 항목 목록을 조회합니다.", tags=["Docents"]),
    retrieve=extend_schema(description="도슨트 항목 상세 정보를 조회합니다.", tags=["Docents"]),
    create=extend_schema(description="새로운 도슨트 하이라이트를 생성합니다.", tags=["Docents"]),
    update=extend_schema(description="도슨트 하이라이트 정보를 업데이트합니다.", tags=["Docents"]),
    partial_update=extend_schema(description="도슨트 하이라이트 정보를 부분 업데이트합니다.", tags=["Docents"]),
    destroy=extend_schema(description="도슨트 하이라이트를 삭제합니다.", tags=["Docents"])
)
class DocentItemViewSet(viewsets.ModelViewSet):
    queryset = DocentItem.objects.all()
    serializer_class = DocentItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['docent', 'artwork']
    ordering_fields = ['order', 'duration']


@extend_schema_view(
    list=extend_schema(description="도슨트 하이라이트 목록을 조회합니다.", tags=["Docents"]),
    retrieve=extend_schema(description="도슨트 하이라이트 상세 정보를 조회합니다.", tags=["Docents"]),
    create=extend_schema(description="새로운 도슨트 하이라이트를 생성합니다.", tags=["Docents"]),
    update=extend_schema(description="도슨트 하이라이트 정보를 업데이트합니다.", tags=["Docents"]),
    partial_update=extend_schema(description="도슨트 하이라이트 정보를 부분 업데이트합니다.", tags=["Docents"]),
    destroy=extend_schema(description="도슨트 하이라이트를 삭제합니다.", tags=["Docents"])
)
class DocentHighlightViewSet(viewsets.ModelViewSet):
    queryset = DocentHighlight.objects.all()
    serializer_class = DocentHighlightSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['docent', 'docent_item', 'color', 'user', 'is_public']
    ordering_fields = ['start_position', 'created_at']
    
    def get_queryset(self):
        """사용자가 볼 수 있는 하이라이트만 반환"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_authenticated:
            # 자신의 하이라이트 + 공개된 하이라이트
            return queryset.filter(
                models.Q(user=user) | models.Q(is_public=True)
            )
        else:
            # 비로그인 사용자는 공개된 하이라이트만 볼 수 있음
            return queryset.filter(is_public=True)
    
    def perform_create(self, serializer):
        """하이라이트 생성 시 현재 사용자 정보 추가"""
        serializer.save(user=self.request.user)
