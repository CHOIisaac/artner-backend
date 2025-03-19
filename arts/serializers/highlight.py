from rest_framework import serializers
from ..models import Highlight


class HighlightSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    artwork_title = serializers.CharField(source='artwork.title', read_only=True)
    artwork_image = serializers.ImageField(source='artwork.image', read_only=True)
    
    class Meta:
        model = Highlight
        fields = '__all__' 