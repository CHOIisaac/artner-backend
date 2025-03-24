from rest_framework import serializers
from .models import Collection, CollectionItem
from artworks.serializers import ArtworkSerializer


class CollectionItemSerializer(serializers.ModelSerializer):
    """컬렉션 항목 정보를 위한 시리얼라이저"""
    class Meta:
        model = CollectionItem
        fields = ['id', 'collection', 'artwork', 'note', 'order', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CollectionSerializer(serializers.ModelSerializer):
    """컬렉션 정보를 위한 시리얼라이저"""
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Collection
        fields = ['id', 'title', 'description', 'user', 'thumbnail_image', 'is_public', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_item_count(self, obj):
        return obj.items.count()


class CollectionDetailedSerializer(serializers.ModelSerializer):
    """컬렉션 상세 정보를 위한 시리얼라이저"""
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = Collection
        fields = ['id', 'title', 'description', 'user', 'thumbnail_image', 'is_public', 'items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_items(self, obj):
        items = obj.items.all().order_by('order')
        return CollectionItemDetailSerializer(items, many=True).data


class CollectionItemDetailSerializer(serializers.ModelSerializer):
    """컬렉션 항목 상세 정보를 위한 시리얼라이저"""
    artwork_detail = ArtworkSerializer(source='artwork', read_only=True)
    
    class Meta:
        model = CollectionItem
        fields = ['id', 'collection', 'artwork', 'artwork_detail', 'note', 'order', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']