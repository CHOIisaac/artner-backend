from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Highlight


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