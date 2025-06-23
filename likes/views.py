from django.shortcuts import render
from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from artists.models import Artist, ArtistLike
from artworks.models import Artwork, ArtworkLike
from exhibitions.models import Exhibition, ExhibitionLike
from .serializers import LikedItemSerializer, LikedItemsResponseSerializer


@extend_schema_view(
    list=extend_schema(
        summary="좋아요 항목 목록 조회",
        description="사용자가 좋아요한 작가, 작품, 전시회 목록을 조회합니다.",
        responses={200: LikedItemsResponseSerializer},
        tags=["Likes"]
    )
)
class LikedItemsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    좋아요한 항목 조회 서비스 (CQRS 패턴의 Query 부분)
    
    사용자가 좋아요한 모든 항목을 조회합니다.
    좋아요 추가/삭제는 각 도메인 앱(artists, artworks, exhibitions)의 API를 통해 수행됩니다.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['-created_at']
    
    def list(self, request, *args, **kwargs):
        """
        사용자가 좋아요한 모든 항목을 조회합니다.
        
        ?type= 쿼리 파라미터로 특정 타입(artist, artwork, exhibition)만 필터링할 수 있습니다.
        """
        user = request.user
        item_type = request.query_params.get('type')  # artist, artwork, exhibition
        
        liked_items = []
        
        # 작가 좋아요 항목 추가 (타입 필터링이 없거나 artist인 경우)
        if not item_type or item_type == 'artist':
            # select_related로 N+1 쿼리 방지
            artist_likes = ArtistLike.objects.filter(user=user).select_related('artist').order_by('-created_at')
            for like in artist_likes:
                artist = like.artist
                liked_items.append({
                    'id': artist.id,
                    'title': artist.name,
                    'description': artist.life_period,
                    'image': artist.image,
                    'type': 'artist',
                    'likes_count': artist.likes_count,
                    'created_at': like.created_at,  # like의 생성일 사용
                    'name': artist.name,
                    'life_period': artist.life_period
                })
        
        # 작품 좋아요 항목 추가 (타입 필터링이 없거나 artwork인 경우)
        if not item_type or item_type == 'artwork':
            # select_related로 N+1 쿼리 방지
            artwork_likes = ArtworkLike.objects.filter(user=user).select_related('artwork').order_by('-created_at')
            for like in artwork_likes:
                artwork = like.artwork
                liked_items.append({
                    'id': artwork.id,
                    'title': artwork.title,
                    'description': artwork.description,
                    'image': artwork.image,
                    'type': 'artwork',
                    'likes_count': artwork.likes_count,
                    'created_at': like.created_at,  # like의 생성일 사용
                    'artist_name': artwork.artist_name,
                    'created_year': artwork.created_year
                })
        
        # 전시회 좋아요 항목 추가 (타입 필터링이 없거나 exhibition인 경우)
        if not item_type or item_type == 'exhibition':
            # select_related로 N+1 쿼리 방지
            exhibition_likes = ExhibitionLike.objects.filter(user=user).select_related('exhibition').order_by('-created_at')
            for like in exhibition_likes:
                exhibition = like.exhibition
                liked_items.append({
                    'id': exhibition.id,
                    'title': exhibition.title,
                    'description': exhibition.description,
                    'image': exhibition.image,
                    'type': 'exhibition',
                    'likes_count': exhibition.likes_count,
                    'created_at': like.created_at,  # like의 생성일 사용
                    'venue': exhibition.venue,
                    'start_date': exhibition.start_date,
                    'end_date': exhibition.end_date,
                    'status': exhibition.status
                })
        
        # 이미 생성일순으로 조회했으므로 정렬 불필요
        # 시리얼라이저로 데이터 검증 및 반환
        serializer = LikedItemsResponseSerializer({
            'liked_items': liked_items
        })
        
        return Response(serializer.data)
