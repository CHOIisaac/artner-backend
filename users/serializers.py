from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보를 위한 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'profile_image', 'bio', 'preferences', 'date_joined']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }