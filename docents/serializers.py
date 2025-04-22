from rest_framework import serializers
from .models import Docent, DocentItem, DocentHighlight
from artworks.serializers import ArtworkSerializer


class DocentItemSerializer(serializers.ModelSerializer):
    artwork_detail = ArtworkSerializer(source='artwork', read_only=True)
    
    class Meta:
        model = DocentItem
        fields = '__all__'


class DocentHighlightSerializer(serializers.ModelSerializer):
    """도슨트 하이라이트 정보를 위한 시리얼라이저"""
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = DocentHighlight
        fields = [
            'id', 'docent', 'docent_item', 'text', 
            'start_position', 'end_position', 
            'user', 'username', 'note', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'username']


class DocentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docent
        fields = '__all__'


class DocentDetailedSerializer(serializers.ModelSerializer):
    """도슨트 상세 정보를 위한 시리얼라이저"""
    items = serializers.SerializerMethodField()
    highlights = DocentHighlightSerializer(many=True, read_only=True)
    
    class Meta:
        model = Docent
        fields = ['id', 'title', 'description', 'type', 'creator', 'exhibition', 
                  'duration', 'is_public', 'view_count', 'like_count', 
                  'items', 'highlights', 'created_at', 'updated_at']
        read_only_fields = ['view_count', 'like_count', 'created_at', 'updated_at']
    
    def get_items(self, obj):
        items = obj.items.all().order_by('order')
        return DocentItemDetailSerializer(items, many=True).data


class DocentItemDetailSerializer(serializers.ModelSerializer):
    """도슨트 항목 상세 정보를 위한 시리얼라이저"""
    artwork_detail = ArtworkSerializer(source='artwork', read_only=True)
    
    class Meta:
        model = DocentItem
        fields = '__all__' 