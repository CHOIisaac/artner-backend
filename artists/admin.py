from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, ArtistLike


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'life_period', 'representative_work', 'preview_image', 'is_featured', 'likes_count')
    search_fields = ('name', 'representative_work')
    list_filter = ('is_featured',)
    readonly_fields = ('preview_image_large', 'likes_count')
    
    fieldsets = [
        (None, {'fields': ['name', 'life_period', 'representative_work']}),
        ('이미지', {'fields': ['image', 'preview_image_large']}),
        ('특성', {'fields': ['is_featured', 'likes_count']}),
    ]
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" />', obj.image.url)
        return "이미지 없음"
    preview_image.short_description = '이미지'
    
    def preview_image_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" />', obj.image.url)
        return "이미지 없음"
    preview_image_large.short_description = '이미지 미리보기'


admin.site.register(ArtistLike)
