from rest_framework import serializers
from ..models import Docent


class DocentSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    exhibition_title = serializers.CharField(source='exhibition.title', read_only=True)
    
    class Meta:
        model = Docent
        fields = '__all__' 