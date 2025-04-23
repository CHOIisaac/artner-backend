from rest_framework import serializers
from artworks.serializers import ArtworkSerializer
from exhibitions.serializers import ExhibitionSerializer

# 요청 및 응답을 위한 간단한 시리얼라이저
class ChatQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True, help_text='사용자 질문')

class ChatResponseSerializer(serializers.Serializer):
    query = serializers.CharField(read_only=True, help_text='사용자 질문')
    response = serializers.CharField(read_only=True, help_text='AI 응답')
    related_artwork = ArtworkSerializer(read_only=True, required=False)
    related_exhibition = ExhibitionSerializer(read_only=True, required=False) 