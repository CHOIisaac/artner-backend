from rest_framework import serializers
from .models import Collection, CollectionItem
from artworks.serializers import ArtworkSerializer

class CollectionItemSerializer(serializers.ModelSerializer):
    artwork_detail = ArtworkSerializer(source='artwork', read_only=True)
    
    class Meta:
        model = CollectionItem
        fields = '__all__'

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'

class CollectionDetailedSerializer(serializers.ModelSerializer):
    items = CollectionItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Collection
        fields = '__all__' 