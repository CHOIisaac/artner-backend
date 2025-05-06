from django.contrib import admin
from django.utils.html import format_html
from .models import Artwork, ArtworkLike


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_name', 'created_year', 'preview_image', 'likes_count')
    search_fields = ('title', 'artist_name', 'description')
    readonly_fields = ('preview_image_large', 'likes_count')
    
    fieldsets = [
        (None, {'fields': ['title', 'artist_name', 'created_year']}),
        ('정보', {'fields': ['description']}),
        ('이미지', {'fields': ['image']}),
        ('통계', {'fields': ['likes_count']}),
    ]
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" />', obj.image.url)
        return "이미지 없음"
    preview_image.short_description = '이미지'
    
    def preview_image_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" />', obj.image.url)
        return "이미지 없음"
    preview_image_large.short_description = '이미지 미리보기'


admin.site.register(ArtworkLike)
