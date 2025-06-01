from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from .models import Highlight, HighlightedText


class HighlightSerializer(serializers.ModelSerializer):
    content_type_str = serializers.SerializerMethodField()

    class Meta:
        model = Highlight
        fields = [
            'id', 'title', 'description', 'content_type', 'content_type_str',
            'object_id', 'order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_content_type_str(self, obj):
        return obj.content_type.model

    def validate(self, data):
        """
        컨텐츠 타입이 유효한지 검증합니다.
        """
        content_type = data.get('content_type')
        if content_type and content_type.model not in ['exhibition', 'artwork']:
            raise serializers.ValidationError("잘못된 컨텐츠 타입입니다. 전시회 또는 작품만 하이라이트에 등록할 수 있습니다.")
        return data


class HighlightedTextSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    related_to = serializers.SerializerMethodField()
    
    class Meta:
        model = HighlightedText
        fields = [
            'id', 'text', 'start_index', 'end_index', 
            'type', 'related_to', 'created_at'
        ]
        read_only_fields = ['created_at', 'type', 'related_to']
        extra_kwargs = {
            'start_index': {'write_only': True},
            'end_index': {'write_only': True},
        }
    
    def get_type(self, obj):
        """
        객체 타입을 반환합니다 (artist 또는 artwork).
        """
        if obj.artist:
            return 'artist'
        elif obj.artwork:
            return 'artwork'
        return None
    
    def get_related_to(self, obj):
        """
        연결된 객체 정보를 반환합니다.
        """
        if obj.artist:
            return {
                'id': obj.artist.id,
                'name': obj.artist.name,
                'type': 'artist'
            }
        elif obj.artwork:
            return {
                'id': obj.artwork.id,
                'name': obj.artwork.title,
                'type': 'artwork'
            }
        return None
    
    def validate(self, data):
        """
        작가와 작품 중 하나만 선택되었는지 검증합니다.
        """
        artist = data.get('artist')
        artwork = data.get('artwork')
        
        if bool(artist) == bool(artwork):
            raise serializers.ValidationError("작가 또는 작품 중 하나만 선택해야 합니다.")
        
        return data
    
    def to_representation(self, instance):
        """
        응답 데이터 형식을 커스터마이징합니다.
        """
        data = super().to_representation(instance)
        
        # 클라이언트에 전달할 간결한 형태로 변환
        return {
            'id': data['id'],
            'text': data['text'],
            'type': data['type'],
            'related_to': data['related_to'],
            'created_at': data['created_at']
        }