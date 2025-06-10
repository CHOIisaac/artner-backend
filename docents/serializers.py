from rest_framework import serializers
from .models import DocentHighlight, SaveFolder, SavedItem
from artworks.serializers import ArtworkSerializer


class SaveFolderSerializer(serializers.ModelSerializer):
    """저장 폴더 시리얼라이저"""
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = SaveFolder
        fields = ['id', 'name', 'description', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'item_count']

    def get_item_count(self, obj):
        """폴더 내 저장된 항목 수를 반환"""
        return obj.items.count()


class SavedItemSerializer(serializers.ModelSerializer):
    """저장 항목 기본 시리얼라이저"""
    folder_name = serializers.CharField(source='folder.name', read_only=True)

    class Meta:
        model = SavedItem
        fields = [
            'id', 'folder', 'folder_name', 'item_type',
            'title', 'life_period', 'artist_name',
            'notes', 'thumbnail', 'created_at'
        ]
        read_only_fields = ['created_at', 'folder_name']


class SavedItemCreateSerializer(serializers.ModelSerializer):
    """저장 항목 생성용 시리얼라이저"""

    class Meta:
        model = SavedItem
        fields = [
            'folder', 'item_type', 'title',
            'life_period', 'artist_name', 'notes', 'thumbnail'
        ]

    def validate(self, data):
        """폴더 접근 권한 및 필수 필드 검증"""
        user = self.context['request'].user
        folder = data.get('folder')
        item_type = data.get('item_type')

        # 폴더 접근 권한 확인
        if folder.user != user:
            raise serializers.ValidationError({"folder": "접근 권한이 없는 폴더입니다."})

        # 항목 유형별 필수 필드 검증
        if item_type == 'artist' and not data.get('title'):
            raise serializers.ValidationError({"title": "작가명은 필수 항목입니다."})

        if item_type == 'artwork':
            if not data.get('title'):
                raise serializers.ValidationError({"title": "작품명은 필수 항목입니다."})
            if not data.get('artist_name'):
                raise serializers.ValidationError({"artist_name": "작가명은 필수 항목입니다."})

        return data


class SavedItemDetailSerializer(serializers.ModelSerializer):
    """저장 항목 상세 시리얼라이저"""
    folder_name = serializers.CharField(source='folder.name', read_only=True)

    class Meta:
        model = SavedItem
        fields = [
            'id', 'folder', 'folder_name', 'item_type',
            'title', 'life_period', 'artist_name',
            'notes', 'thumbnail', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'folder_name']


class DocentHighlightSerializer(serializers.ModelSerializer):
    """도슨트 하이라이트 정보를 위한 시리얼라이저"""
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = DocentHighlight
        fields = [
            'id', 'docent', 'docent_item', 'text', 
            'start_position', 'end_position', 
            'user', 'username', 'note', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'username']



