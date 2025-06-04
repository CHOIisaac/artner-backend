from django.contrib import admin
from .models import ExhibitionRecord


@admin.register(ExhibitionRecord)
class ExhibitionRecordAdmin(admin.ModelAdmin):
    """전시 기록 관리자"""
    list_display = ('user', 'name', 'museum', 'visit_date', 'created_at')
    list_filter = ('visit_date', 'created_at')
    search_fields = ('user__username', 'name', 'museum')
    readonly_fields = ('created_at', 'updated_at')
