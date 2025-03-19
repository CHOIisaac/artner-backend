from rest_framework import serializers
from ..models import Exhibition
from .artwork import ArtworkSerializer


class ExhibitionSerializer(serializers.ModelSerializer):
    museum_name = serializers.CharField(source='museum.name', read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Exhibition
        fields = '__all__'


class ExhibitionDetailSerializer(ExhibitionSerializer):
    artworks = ArtworkSerializer(many=True, read_only=True)
    
    class Meta(ExhibitionSerializer.Meta):
        fields = ExhibitionSerializer.Meta.fields + ('artworks',) 