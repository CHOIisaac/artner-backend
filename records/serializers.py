from rest_framework import serializers
from .models import ExhibitionRecord


class ExhibitionRecordSerializer(serializers.ModelSerializer):
    """전시 기록 시리얼라이저"""
    
    class Meta:
        model = ExhibitionRecord
        fields = [
            'id', 'user', 'visit_date', 'name', 'museum', 
            'note', 'image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """사용자 정보 추가"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExhibitionRecordCreateSerializer(serializers.ModelSerializer):
    """전시 기록 생성 시리얼라이저"""
    class Meta:
        model = ExhibitionRecord
        fields = ['visit_date', 'name', 'museum', 'note', 'image']
    
    def create(self, validated_data):
        """사용자 정보 추가"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 