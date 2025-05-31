from django.contrib import admin
from .models import Highlight

@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'object_id', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'content_type')
    search_fields = ('title', 'description')
    ordering = ('order', '-created_at')