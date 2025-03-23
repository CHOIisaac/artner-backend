from rest_framework import serializers
from .models import Artwork, ArtworkDetail

class ArtworkDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtworkDetail
        fields = '__all__'

class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = '__all__'

class ArtworkDetailedSerializer(serializers.ModelSerializer):
    detail = ArtworkDetailSerializer(read_only=True)
    
    class Meta:
        model = Artwork
        fields = '__all__' 