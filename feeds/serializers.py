from rest_framework import serializers


class FeedItemSerializer(serializers.Serializer):
    """피드 항목 시리얼라이저"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    image = serializers.ImageField(allow_null=True)
    type = serializers.CharField()  # 'artist', 'artwork', 'exhibition' 중 하나
    likes_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    
    # 작가용 필드
    name = serializers.CharField(required=False, allow_blank=True)
    life_period = serializers.CharField(required=False, allow_blank=True)
    representative_work = serializers.CharField(required=False, allow_blank=True)
    
    # 작품용 필드
    artist_name = serializers.CharField(required=False, allow_blank=True)
    created_year = serializers.CharField(required=False, allow_blank=True)
    
    # 전시회용 필드
    venue = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True)


class FeedResponseSerializer(serializers.Serializer):
    """피드 응답 시리얼라이저"""
    feed_items = FeedItemSerializer(many=True) 