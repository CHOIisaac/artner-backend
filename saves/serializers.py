from rest_framework import serializers
from .models import SaveFolder, SaveItem
from artists.serializers import ArtistSerializer
from artworks.serializers import ArtworkSerializer
from exhibitions.serializers import ExhibitionSerializer


class SaveFolderSerializer(serializers.ModelSerializer):
    """저장 폴더 시리얼라이저"""
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SaveFolder
        fields = ['id', 'name', 'description', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_item_count(self, obj):
        """폴더 내 저장된 항목 수를 반환"""
        return obj.items.count()


class SaveItemSerializer(serializers.ModelSerializer):
    """저장 항목 기본 시리얼라이저"""
    class Meta:
        model = SaveItem
        fields = ['id', 'folder', 'item_type', 'item_id', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SaveItemDetailSerializer(serializers.ModelSerializer):
    """저장 항목 상세 시리얼라이저 (저장된 항목의 세부 정보 포함)"""
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    item_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = SaveItem
        fields = ['id', 'folder', 'folder_name', 'item_type', 'item_id', 'notes', 
                  'item_detail', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'folder_name', 'item_detail']
    
    def get_item_detail(self, obj):
        """저장된 항목의 세부 정보를 반환"""
        item = obj.item
        if not item:
            return None
        
        if obj.item_type == 'artist':
            return ArtistSerializer(item).data
        elif obj.item_type == 'artwork':
            return ArtworkSerializer(item).data
        elif obj.item_type == 'exhibition':
            return ExhibitionSerializer(item).data
        return None


class CreateSaveItemSerializer(serializers.ModelSerializer):
    """저장 항목 생성용 시리얼라이저"""
    class Meta:
        model = SaveItem
        fields = ['folder', 'item_type', 'item_id', 'notes']
    
    def validate(self, data):
        """저장하려는 항목(작가, 작품, 전시회)이 실제로 존재하는지 확인"""
        item_type = data.get('item_type')
        item_id = data.get('item_id')
        
        # 항목 유형에 따라 해당 객체가 존재하는지 확인
        if item_type == 'artist':
            from artists.models import Artist
            if not Artist.objects.filter(id=item_id).exists():
                raise serializers.ValidationError({'item_id': '해당 ID의 작가가 존재하지 않습니다.'})
        elif item_type == 'artwork':
            from artworks.models import Artwork
            if not Artwork.objects.filter(id=item_id).exists():
                raise serializers.ValidationError({'item_id': '해당 ID의 작품이 존재하지 않습니다.'})
        elif item_type == 'exhibition':
            from exhibitions.models import Exhibition
            if not Exhibition.objects.filter(id=item_id).exists():
                raise serializers.ValidationError({'item_id': '해당 ID의 전시회가 존재하지 않습니다.'})
        else:
            raise serializers.ValidationError({'item_type': '유효하지 않은 항목 유형입니다.'})
        
        # 사용자가 이 폴더에 접근할 수 있는지 확인
        user = self.context['request'].user
        folder = data.get('folder')
        if folder.user != user:
            raise serializers.ValidationError({'folder': '접근할 수 없는 폴더입니다.'})
        
        return data 