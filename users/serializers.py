from rest_framework import serializers
from .models import User, UserPreference
from collections.serializers import CollectionSerializer
from docents.serializers import DocentSerializer

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'profile_image', 'bio', 'preferences', 'date_joined']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserDetailedSerializer(serializers.ModelSerializer):
    preference_detail = UserPreferenceSerializer(read_only=True)
    collections = CollectionSerializer(many=True, read_only=True)
    docents = DocentSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'profile_image', 'bio', 
                  'preferences', 'date_joined', 'preference_detail', 'collections', 'docents']
        read_only_fields = ['date_joined'] 