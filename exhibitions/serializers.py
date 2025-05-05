from rest_framework import serializers
from .models import Exhibition
from artworks.serializers import ArtworkSerializer


class ExhibitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibition
        fields = '__all__'