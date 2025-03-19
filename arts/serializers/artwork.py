from rest_framework import serializers
from ..models import Artwork


class ArtworkSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    
    class Meta:
        model = Artwork
        fields = '__all__' 