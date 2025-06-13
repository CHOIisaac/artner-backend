from rest_framework import serializers
from .models import Highlight


class HighlightSerializer(serializers.ModelSerializer):
    """하이라이트 시리얼라이저"""

    class Meta:
        model = Highlight
        fields = [
            'id', 'item_type', 'item_name', 'item_info',
            'highlighted_text', 'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class HighlightListSerializer(serializers.ModelSerializer):
    """하이라이트 목록용 간소화된 시리얼라이저"""

    class Meta:
        model = Highlight
        fields = [
            'id', 'item_type', 'item_name', 'item_info',
            'highlighted_text', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """
        item_type이 유효한지 검증합니다.
        """
        item_type = data.get('item_type')
        if item_type not in ['artist', 'artwork']:
            raise serializers.ValidationError("item_type은 'artist' 또는 'artwork'여야 합니다.")
        
        return data
    
    def to_representation(self, instance):
        """
        응답 데이터 형식을 커스터마이징합니다.
        """
        data = super().to_representation(instance)
        
        # 클라이언트에 전달할 간결한 형태로 변환
        return {
            'id': data['id'],
            'text': data['highlighted_text'],
            'type': data['item_type'],
            'related_to': {
                'name': data['item_name'],
                'info': data['item_info']
            },
            'created_at': data['created_at']
        }