from django.db.models import Count, Q, Max
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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
        operation_id="01_highlight_list",
        description="특정 작가 또는 작품에 대한 하이라이트 목록을 조회합니다.",
        tags=["Highlights"]
    ),
    retrieve=extend_schema(
        summary="하이라이트 상세 조회",
        operation_id="03_highlight_retrieve",
        description="특정 하이라이트의 상세 정보를 조회합니다.",
        tags=["Highlights"]
    ),
    create=extend_schema(
        summary="하이라이트 생성",
        operation_id="02_highlight_create",
        description="새로운 하이라이트를 생성합니다.",
        tags=["Highlights"]
    ),
    destroy=extend_schema(
        summary="하이라이트 삭제",
        operation_id="04_highlight_delete",
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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['item_type', 'item_name']
    search_fields = ['highlighted_text', 'item_name', 'note']
    http_method_names = ['get', 'post', 'delete', 'head', 'options']  # PUT, PATCH 제외
    
    def get_queryset(self):
        """
        항상 로그인한 사용자의 하이라이트만 반환
        """
        return Highlight.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """하이라이트 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        summary="하이라이트 통계",
        operation_id="05_highlight_stats",
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
        작가 또는 작품별 하이라이트 개수 통계 (항상 내 하이라이트만)
        """
        item_type = request.query_params.get('type')
        qs = self.get_queryset()
        result = []
        if not item_type or item_type == 'artist':
            artist_highlights = qs.filter(item_type='artist').values('item_name').annotate(highlight_count=Count('id')).order_by('-highlight_count')
            for item in artist_highlights:
                result.append({
                    'name': item['item_name'],
                    'type': 'artist',
                    'count': item['highlight_count']
                })
        if not item_type or item_type == 'artwork':
            artwork_highlights = qs.filter(item_type='artwork').values('item_name').annotate(highlight_count=Count('id')).order_by('-highlight_count')
            for item in artwork_highlights:
                result.append({
                    'name': item['item_name'],
                    'type': 'artwork',
                    'count': item['highlight_count']
                })
        result.sort(key=lambda x: x['count'], reverse=True)
        return Response(result)
    
    @extend_schema(
        summary="전체 텍스트 조회",
        operation_id="06_highlight_context",
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

    @extend_schema(
        summary="도슨트별 하이라이트 그룹 목록",
        operation_id="07_highlight_grouped",
        description="작가 또는 작품별로 하이라이트 개수와 하이라이트 리스트를 반환합니다.",
        parameters=[
            OpenApiParameter(name="item_type", description="항목 유형 (artist, artwork)", required=False, type=str),
        ],
        tags=["Highlights"]
    )
    @action(detail=False, methods=['get'], url_path='grouped')
    def grouped(self, request):
        """
        도슨트(작가/작품)별(타입+이름) 하이라이트 개수와 최근 3개 하이라이트 리스트 반환
        item_type, item_name이 같으면 item_info가 달라도 하나로 묶음
        DB 집계로 성능 개선, 상위 20개 그룹만 반환
        """
        item_type = request.query_params.get('item_type')
        qs = self.get_queryset()
        if item_type:
            qs = qs.filter(item_type=item_type)

        # DB에서 그룹핑/카운트/최신순 정렬, 상위 20개만
        grouped = qs.values('item_type', 'item_name') \
            .annotate(
                highlight_count=Count('id'),
                latest_created=Max('created_at')
            ) \
            .order_by('-latest_created')[:20]

        result = []
        for group in grouped:
            item_type = group['item_type']
            item_name = group['item_name']
            highlight_count = group['highlight_count']
            # 대표 item_info: 최신 하이라이트의 값
            latest_highlight = qs.filter(item_type=item_type, item_name=item_name).order_by('-created_at').first()
            item_info = latest_highlight.item_info if latest_highlight else ''
            # 최근 3개 하이라이트만
            highlights = qs.filter(item_type=item_type, item_name=item_name).order_by('-created_at')[:3]
            result.append({
                'item_type': item_type,
                'item_name': item_name,
                'item_info': item_info,
                'highlight_count': highlight_count,
                'highlights': HighlightSerializer(highlights, many=True).data
            })
        return Response(result)
