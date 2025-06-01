from django.contrib import admin
from .models import Highlight, HighlightedText

@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'object_id', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'content_type')
    search_fields = ('title', 'description')
    ordering = ('order', '-created_at')

@admin.register(HighlightedText)
class HighlightedTextAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'content_type_display', 'content_object_display', 'created_at')
    list_filter = ('artist__isnull', 'artwork__isnull')
    search_fields = ('text', 'artist__name', 'artwork__title')
    ordering = ('-created_at',)
    
    def text_preview(self, obj):
        """텍스트 미리보기 (최대 50자)"""
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    
    def content_type_display(self, obj):
        """콘텐츠 타입 표시"""
        return obj.content_type_str.capitalize() if obj.content_type_str else 'Unknown'
    content_type_display.short_description = '콘텐츠 타입'
    
    def content_object_display(self, obj):
        """콘텐츠 객체 표시"""
        if obj.artist:
            return f"{obj.artist.name}"
        elif obj.artwork:
            return f"{obj.artwork.title}"
        return 'Unknown'
    content_object_display.short_description = '관련 객체'