from rest_framework import serializers
from ..models import Collection, CollectionItem


class CollectionSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Collection
        fields = '__all__'
        read_only_fields = ('user',)
    
    def get_item_count(self, obj):
        return obj.items.count()


class CollectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = '__all__'
        read_only_fields = ('collection',) 