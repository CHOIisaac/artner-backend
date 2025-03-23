from rest_framework import serializers
from .models import Exhibition, ExhibitionDetail
from artworks.serializers import ArtworkSerializer

class ExhibitionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExhibitionDetail
        fields = '__all__'

class ExhibitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibition
        fields = '__all__'

class ExhibitionDetailedSerializer(serializers.ModelSerializer):
    detail = ExhibitionDetailSerializer(read_only=True)
    artworks = ArtworkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exhibition
        fields = '__all__' 