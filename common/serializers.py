from rest_framework import serializers
from .models import Tag, Review
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']

@extend_schema_serializer(
    description="리뷰 정보를 위한 시리얼라이저"
)
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'content_type', 'object_id', 'content', 'rating', 'created_at']
    
    @extend_schema_field(serializers.CharField(description="리뷰 작성자 이름"))
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None 