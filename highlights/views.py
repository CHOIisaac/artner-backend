from django.db.models import Count, Q
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
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
    ),
    retrieve=extend_schema(
        summary="하이라이트 상세 조회",
        description="특정 하이라이트의 상세 정보를 조회합니다.",
    ),
    create=extend_schema(
        summary="하이라이트 생성",
        description="새로운 하이라이트를 생성합니다.",
    ),
    destroy=extend_schema(
        summary="하이라이트 삭제",
        description="하이라이트를 삭제합니다.",
    ),
)
class HighlightedTextViewSet(viewsets.ModelViewSet):
    """
    LLM 응답에서 하이라이트된 텍스트를 관리하는 API
    """
    queryset = Highlight.objects.all()
    serializer_class = HighlightSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['artist', 'artwork']
    search_fields = ['text']
    http_method_names = ['get', 'post', 'delete', 'head', 'options']  # PUT, PATCH 제외
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 컨텐츠 타입 필터링
        content_type = self.request.query_params.get('type')
        if content_type:
            if content_type == 'artist':
                queryset = queryset.filter(artist__isnull=False)
            elif content_type == 'artwork':
                queryset = queryset.filter(artwork__isnull=False)
            
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
                artist__isnull=False
            ).values('artist').annotate(
                highlight_count=Count('id')
            ).order_by('-highlight_count')
            
            for item in artist_highlights:
                try:
                    artist = Artist.objects.get(id=item['artist'])
                    result.append({
                        'id': artist.id,
                        'name': artist.name,
                        'type': 'artist',
                        'count': item['highlight_count']
                    })
                except Artist.DoesNotExist:
                    pass
        
        # 작품 관련 하이라이트 집계
        if not content_type or content_type == 'artwork':
            artwork_highlights = Highlight.objects.filter(
                artwork__isnull=False
            ).values('artwork').annotate(
                highlight_count=Count('id')
            ).order_by('-highlight_count')
            
            for item in artwork_highlights:
                try:
                    artwork = Artwork.objects.get(id=item['artwork'])
                    result.append({
                        'id': artwork.id,
                        'name': artwork.title,
                        'type': 'artwork',
                        'count': item['highlight_count']
                    })
                except Artwork.DoesNotExist:
                    pass
        
        # 정렬
        result.sort(key=lambda x: x['count'], reverse=True)
        
        return Response(result)
    
    @extend_schema(
        summary="전체 텍스트 조회",
        description="하이라이트가 포함된 전체 LLM 응답을 조회합니다.",
    )
    @action(detail=True, methods=['get'], url_path='context')
    def context(self, request, pk=None):
        """
        하이라이트가 포함된 전체 LLM 응답 컨텍스트를 조회합니다.
        """
        highlighted_text = self.get_object()
        
        # 연결된 객체 정보
        related_object = None
        object_type = None
        
        if highlighted_text.artist:
            related_object = highlighted_text.artist.name
            object_type = 'artist'
        elif highlighted_text.artwork:
            related_object = highlighted_text.artwork.title
            object_type = 'artwork'
            
        return Response({
            'text': highlighted_text.llm_response,
            'highlight': {
                'text': highlighted_text.text,
                'start': highlighted_text.start_index,
                'end': highlighted_text.end_index,
            },
            'related_to': {
                'id': highlighted_text.artist_id or highlighted_text.artwork_id,
                'name': related_object,
                'type': object_type
            }
        })
