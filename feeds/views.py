from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view
from artists.models import Artist
from artworks.models import Artwork
from exhibitions.models import Exhibition
from .serializers import FeedResponseSerializer
import random


@extend_schema_view(
    list=extend_schema(
        summary="피드 정보 조회",
        description="피드 정보를 가져옵니다. 작가, 작품, 전시회를 랜덤하게 조합하여 12개의 항목을 반환합니다.",
        responses={200: FeedResponseSerializer},
        tags=["Feed"]
    )
)
class FeedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    사용자 피드를 위한 ViewSet.
    작가, 작품, 전시회를 랜덤하게 조합하여 12개의 항목을 반환합니다.
    """
    permission_classes = [AllowAny]  # 인증 없이 접근 가능
    
    def list(self, request, *args, **kwargs):
        # 각 모델에서 랜덤 데이터 효율적으로 가져오기
        # 고정된 수량 설정 (각 모델별로 4개씩 = 총 12개)
        artist_count = 4
        artwork_count = 4
        exhibition_count = 4
        
        # 최적화된 랜덤 조회 사용
        random_artists = Artist.objects.random(artist_count)
        random_artworks = Artwork.objects.random(artwork_count)
        random_exhibitions = Exhibition.objects.random(exhibition_count)
        
        feed_items = []
        
        # 작가 데이터 변환
        for artist in random_artists:
            feed_items.append({
                'id': artist.id,
                'title': artist.name,
                'description': artist.life_period,
                'image': artist.image,
                'type': 'artist',
                'likes_count': artist.likes_count,
                'created_at': artist.created_at,
                'name': artist.name,
                'life_period': artist.life_period,
                'representative_work': artist.representative_work
            })
        
        # 작품 데이터 변환
        for artwork in random_artworks:
            feed_items.append({
                'id': artwork.id,
                'title': artwork.title,
                'description': artwork.description,
                'image': artwork.image,
                'type': 'artwork',
                'likes_count': artwork.likes_count,
                'created_at': artwork.created_at,
                'artist_name': artwork.artist_name,
                'created_year': artwork.created_year
            })
        
        # 전시회 데이터 변환
        for exhibition in random_exhibitions:
            feed_items.append({
                'id': exhibition.id,
                'title': exhibition.title,
                'description': exhibition.description,
                'image': exhibition.image,
                'type': 'exhibition',
                'likes_count': exhibition.likes_count,
                'created_at': exhibition.created_at,
                'venue': exhibition.venue,
                'start_date': exhibition.start_date,
                'end_date': exhibition.end_date,
                'status': exhibition.status
            })
        
        # 항목 랜덤하게 섞기
        random.shuffle(feed_items)
        
        # 시리얼라이저로 데이터 검증 및 반환
        serializer = FeedResponseSerializer({
            'feed_items': feed_items
        })
        
        return Response(serializer.data)
