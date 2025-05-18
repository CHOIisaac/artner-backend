from rest_framework import serializers
from .models import Artist


class ArtistSerializer(serializers.ModelSerializer):
    """작가 정보를 위한 시리얼라이저"""
    
    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'life_period', 'representative_work', 
            'image', 'likes_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['likes_count', 'created_at', 'updated_at']


class ArtistDetailedSerializer(serializers.ModelSerializer):
    """작가 상세 정보를 위한 시리얼라이저"""
    
    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'life_period', 'representative_work', 
            'image', 'likes_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['likes_count', 'created_at', 'updated_at'] 