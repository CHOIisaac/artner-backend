from rest_framework import serializers
from .models import Docent, DocentItem
from artworks.serializers import ArtworkSerializer

class DocentItemSerializer(serializers.ModelSerializer):
    artwork_detail = ArtworkSerializer(source='artwork', read_only=True)
    
    class Meta:
        model = DocentItem
        fields = '__all__'

class DocentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docent
        fields = '__all__'

class DocentDetailedSerializer(serializers.ModelSerializer):
    items = DocentItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Docent
        fields = '__all__' 