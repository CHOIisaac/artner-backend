from rest_framework import serializers
from .models import Folder, Docent


class FolderSerializer(serializers.ModelSerializer):
    """폴더 시리얼라이저"""
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'items_count']

    def get_items_count(self, obj):
        """폴더 내 항목 수를 반환
        
        성능 최적화:
        - ViewSet에서 Folder.objects.prefetch_related('docents') 사용 권장
        - 또는 annotate(items_count=Count('docents')) 사용 권장
        """
        # prefetch된 경우 len() 사용 (추가 쿼리 없음)
        if hasattr(obj, '_prefetched_objects_cache') and 'docents' in obj._prefetched_objects_cache:
            return len(obj.docents.all())
        # 그렇지 않으면 count() 사용
        return obj.docents.count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DocentSerializer(serializers.ModelSerializer):
    """폴더 항목 기본 시리얼라이저"""
    folder_name = serializers.CharField(source='folder.name', read_only=True)

    class Meta:
        model = Docent
        fields = ['id', 'folder', 'folder_name', 'item_type', 'title', 'life_period', 
                 'artist_name', 'script', 'notes', 'thumbnail', 'created_at', 'updated_at']
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DocentCreateSerializer(serializers.ModelSerializer):
    """폴더 항목 생성용 시리얼라이저"""

    class Meta:
        model = Docent
        fields = ['folder', 'item_type', 'title', 'life_period', 'artist_name', 'script', 'notes', 'thumbnail']

    def validate_folder(self, value):
        # 폴더가 현재 사용자의 것인지 확인
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("다른 사용자의 폴더에는 저장할 수 없습니다.")
        return value

    def validate(self, attrs):
        # 작가일 경우 life_period가 있어야 하고, 작품일 경우 artist_name이 있어야 함
        item_type = attrs.get('item_type')
        if item_type == 'artist':
            if not attrs.get('life_period'):
                attrs['life_period'] = ''  # 빈 문자열로 설정
        elif item_type == 'artwork':
            if not attrs.get('artist_name'):
                attrs['artist_name'] = ''  # 빈 문자열로 설정

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DocentDetailSerializer(serializers.ModelSerializer):
    """폴더 항목 상세 시리얼라이저"""
    folder_name = serializers.CharField(source='folder.name', read_only=True)

    class Meta:
        model = Docent
        fields = ['id', 'folder', 'folder_name', 'item_type', 'title', 'life_period', 
                 'artist_name', 'script', 'notes', 'thumbnail', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'folder_name']


class FolderDetailSerializer(serializers.ModelSerializer):
    docents = DocentDetailSerializer(many=True, read_only=True)
    docents_count = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'docents', 'docents_count']

    def get_docents_count(self, obj):
        """폴더 내 도슨트 수를 반환
        
        성능 최적화: 이미 docents를 prefetch했으므로 len() 사용
        """
        if hasattr(obj, '_prefetched_objects_cache') and 'docents' in obj._prefetched_objects_cache:
            return len(obj.docents.all())
        return obj.docents.count()









