from rest_framework import serializers
from exhibitions.models import ExhibitionLike
from artworks.models import ArtworkLike
from artists.models import ArtistLike
from exhibitions.serializers import ExhibitionSerializer
from artworks.serializers import ArtworkSerializer
from artists.serializers import ArtistSerializer


class ExhibitionLikeSerializer(serializers.ModelSerializer):
    """전시회 좋아요 시리얼라이저"""
    exhibition_detail = ExhibitionSerializer(source='exhibition', read_only=True)
    
    class Meta:
        model = ExhibitionLike
        fields = ['id', 'user', 'exhibition', 'exhibition_detail', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ArtworkLikeSerializer(serializers.ModelSerializer):
    """작품 좋아요 시리얼라이저"""
    artwork_detail = ArtworkSerializer(source='artwork', read_only=True)
    
    class Meta:
        model = ArtworkLike
        fields = ['id', 'user', 'artwork', 'artwork_detail', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ArtistLikeSerializer(serializers.ModelSerializer):
    """작가 좋아요 시리얼라이저"""
    artist_detail = ArtistSerializer(source='artist', read_only=True)
    
    class Meta:
        model = ArtistLike
        fields = ['id', 'user', 'artist', 'artist_detail', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 