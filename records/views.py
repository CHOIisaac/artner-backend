from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import ExhibitionRecord
from .serializers import (
    ExhibitionRecordSerializer, 
    ExhibitionRecordCreateSerializer, 
    ExhibitionRecordUpdateSerializer
)
from common.mixins import DetailedSerializerMixin


@extend_schema_view(
    list=extend_schema(summary="전시 관람 기록 목록 조회", description="사용자의 전시 관람 기록 목록을 조회합니다.", tags=["Records"]),
    retrieve=extend_schema(summary="전시 관람 기록 상세 조회", description="특정 전시 관람 기록의 상세 정보를 조회합니다.", tags=["Records"]),
    create=extend_schema(summary="전시 관람 기록 생성", description="새로운 전시 관람 기록을 생성합니다.", tags=["Records"]),
    update=extend_schema(summary="전시 관람 기록 전체 수정", description="전시 관람 기록 정보를 업데이트합니다.", tags=["Records"]),
    partial_update=extend_schema(summary="전시 관람 기록 부분 수정", description="전시 관람 기록 정보를 부분 업데이트합니다.", tags=["Records"]),
    destroy=extend_schema(summary="전시 관람 기록 삭제", description="전시 관람 기록을 삭제합니다.", tags=["Records"])
)
class ExhibitionRecordViewSet(DetailedSerializerMixin, viewsets.ModelViewSet):
    """전시 관람 기록 관리 ViewSet"""
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
        elif self.action in ['update', 'partial_update']:
            return ExhibitionRecordUpdateSerializer
        return super().get_serializer_class()
