from django.db.models import Count, Q
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from artists.models import Artist
from artworks.models import Artwork
from .models import Highlight
from .serializers import HighlightSerializer


# Create your views here.

@extend_schema_view(
    list=extend_schema(
        summary="하이라이트 목록 조회",
        description="특정 작가 또는 작품에 대한 하이라이트 목록을 조회합니다.",
        tags=["Highlights"]
    ),
    retrieve=extend_schema(
        summary="하이라이트 상세 조회",
        description="특정 하이라이트의 상세 정보를 조회합니다.",
        tags=["Highlights"]
    ),
    create=extend_schema(
        summary="하이라이트 생성",
        description="새로운 하이라이트를 생성합니다.",
        tags=["Highlights"]
    ),
    destroy=extend_schema(
        summary="하이라이트 삭제",
        description="하이라이트를 삭제합니다.",
        tags=["Highlights"]
    ),
)
class HighlightedTextViewSet(viewsets.ModelViewSet):
    """
    LLM 응답에서 하이라이트된 텍스트를 관리하는 API
    """
    queryset = Highlight.objects.all()
    serializer_class = HighlightSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['item_type', 'item_name']
    search_fields = ['highlighted_text', 'item_name', 'note']
    http_method_names = ['get', 'post', 'delete', 'head', 'options']  # PUT, PATCH 제외
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 컨텐츠 타입 필터링
        content_type = self.request.query_params.get('type')
        if content_type:
            if content_type in ['artist', 'artwork']:
                queryset = queryset.filter(item_type=content_type)
            
        return queryset
    
    @extend_schema(
        summary="하이라이트 통계",
        description="작가 또는 작품별 하이라이트 개수 통계를 제공합니다.",
        parameters=[
            OpenApiParameter(
                name="type",
                description="필터링할 항목 타입 (artist 또는 artwork)",
                required=False,
                type=str,
            ),
        ],
        tags=["Highlights"]
    )
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        작가 또는 작품별 하이라이트 개수 통계를 제공합니다.
        """
        content_type = request.query_params.get('type')
        result = []
        
        # 작가 관련 하이라이트 집계
        if not content_type or content_type == 'artist':
            artist_highlights = Highlight.objects.filter(
                item_type='artist'
            ).values('item_name').annotate(
                highlight_count=Count('id')
            ).order_by('-highlight_count')
            
            for item in artist_highlights:
                result.append({
                    'name': item['item_name'],
                    'type': 'artist',
                    'count': item['highlight_count']
                })
        
        # 작품 관련 하이라이트 집계
        if not content_type or content_type == 'artwork':
            artwork_highlights = Highlight.objects.filter(
                item_type='artwork'
            ).values('item_name').annotate(
                highlight_count=Count('id')
            ).order_by('-highlight_count')
            
            for item in artwork_highlights:
                result.append({
                    'name': item['item_name'],
                    'type': 'artwork',
                    'count': item['highlight_count']
                })
        
        # 정렬
        result.sort(key=lambda x: x['count'], reverse=True)
        
        return Response(result)
    
    @extend_schema(
        summary="전체 텍스트 조회",
        description="하이라이트가 포함된 전체 LLM 응답을 조회합니다.",
        tags=["Highlights"]
    )
    @action(detail=True, methods=['get'], url_path='context')
    def context(self, request, pk=None):
        """
        하이라이트가 포함된 전체 LLM 응답 컨텍스트를 조회합니다.
        """
        highlighted_text = self.get_object()
            
        return Response({
            'text': highlighted_text.highlighted_text,
            'item_type': highlighted_text.item_type,
            'item_name': highlighted_text.item_name,
            'item_info': highlighted_text.item_info,
            'note': highlighted_text.note
        })
