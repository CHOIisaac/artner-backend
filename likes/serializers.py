from rest_framework import serializers
from artists.models import Artist, ArtistLike
from artworks.models import Artwork, ArtworkLike
from exhibitions.models import Exhibition, ExhibitionLike


class LikedItemSerializer(serializers.Serializer):
    """좋아요한 항목을 위한 통합 시리얼라이저"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    image = serializers.URLField(allow_null=True)
    type = serializers.CharField()  # artist, artwork, exhibition
    likes_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    
    # 작가 전용 필드
    name = serializers.CharField(required=False, allow_null=True)
    life_period = serializers.CharField(required=False, allow_null=True)
    
    # 작품 전용 필드
    artist_name = serializers.CharField(required=False, allow_null=True)
    created_year = serializers.CharField(required=False, allow_null=True)
    
    # 전시회 전용 필드
    venue = serializers.CharField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_null=True)


class LikedItemsResponseSerializer(serializers.Serializer):
    """좋아요한 항목 목록 응답을 위한 시리얼라이저"""
    liked_items = LikedItemSerializer(many=True) 