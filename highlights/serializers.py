from rest_framework import serializers
from .models import Highlight


class HighlightSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    related_to = serializers.SerializerMethodField()
    
    class Meta:
        model = Highlight
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