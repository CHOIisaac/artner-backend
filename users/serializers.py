from rest_framework import serializers
from .models import User, UserPreference
from art_collections.serializers import CollectionSerializer
from docents.serializers import DocentSerializer
from drf_spectacular.utils import extend_schema_field


class UserPreferenceSerializer(serializers.ModelSerializer):
    """사용자 취향 정보를 위한 시리얼라이저"""
    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'favorite_artists', 'favorite_genres', 'favorite_periods', 'visit_frequency']


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보를 위한 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'profile_image', 'bio', 'preferences', 'date_joined']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserDetailedSerializer(serializers.ModelSerializer):
    """사용자 상세 정보를 위한 시리얼라이저"""
    preference_detail = UserPreferenceSerializer(read_only=True)
    collections = CollectionSerializer(many=True, read_only=True)
    docents = DocentSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'profile_image', 'bio', 
                    'preferences', 'date_joined', 'preference_detail', 'collections', 'docents', 'last_login']
        read_only_fields = ['date_joined', 'last_login'] 