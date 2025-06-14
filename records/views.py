from rest_framework import filters
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import ExhibitionRecord
from .serializers import (
    ExhibitionRecordSerializer, 
    ExhibitionRecordCreateSerializer
)


@extend_schema_view(
    list=extend_schema(summary="전시 관람 기록 목록 조회", description="사용자의 전시 관람 기록 목록을 조회합니다.", tags=["Records"]),
    create=extend_schema(summary="전시 관람 기록 생성", description="새로운 전시 관람 기록을 생성합니다.", tags=["Records"]),
    destroy=extend_schema(summary="전시 관람 기록 삭제", description="전시 관람 기록을 삭제합니다.", tags=["Records"])
)
class ExhibitionRecordViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    """전시 관람 기록 관리 ViewSet - 목록 조회, 생성, 삭제 기능만 제공"""
    serializer_class = ExhibitionRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """로그인한 사용자의 전시 기록만 반환"""
        return ExhibitionRecord.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """요청 유형에 따라 적절한 시리얼라이저 반환"""
        if self.action == 'create':
            return ExhibitionRecordCreateSerializer
        return self.serializer_class
