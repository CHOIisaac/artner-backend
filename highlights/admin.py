from django.contrib import admin
from .models import Highlight


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'item_type', 'item_name', 'created_at')
    list_filter = ('item_type', 'created_at')
    search_fields = ('highlighted_text', 'item_name', 'note')
    ordering = ('-created_at',)
    
    def text_preview(self, obj):
        """텍스트 미리보기 (최대 50자)"""
        return obj.highlighted_text[:50] + ('...' if len(obj.highlighted_text) > 50 else '')
    text_preview.short_description = '하이라이트 텍스트'
    
    def content_type_display(self, obj):
        """콘텐츠 타입 표시"""
        return obj.get_item_type_display()
    content_type_display.short_description = '콘텐츠 타입'
    
    def content_object_display(self, obj):
        """콘텐츠 객체 표시"""
        return f"{obj.item_name} ({obj.get_item_type_display()})"
    content_object_display.short_description = '관련 객체'