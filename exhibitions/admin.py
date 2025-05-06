from django.contrib import admin
from django.utils.html import format_html
from .models import Exhibition, ExhibitionStatus, ExhibitionLike


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'venue', 'date_range', 'status_display', 'preview_image', 'likes_count']
    list_filter = ['status']
    search_fields = ['title', 'venue', 'description']
    readonly_fields = ['status', 'preview_image_large', 'likes_count']
    date_hierarchy = 'start_date'

    fieldsets = [
        (None, {'fields': ['title', 'description']}),
        ('장소 및 일정', {'fields': ['venue', 'start_date', 'end_date', 'status']}),
        ('추가 정보', {'fields': ['map_url', 'museum_url']}),
        ('이미지', {'fields': ['image', 'preview_image_large']}),
        ('통계', {'fields': ['likes_count']}),
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

    def date_range(self, obj):
        return f"{obj.start_date} ~ {obj.end_date}"
    date_range.short_description = '전시 기간'

    def status_display(self, obj):
        status_colors = {
            ExhibitionStatus.UPCOMING: '#ffc107',  # 예정 - 노란색
            ExhibitionStatus.ONGOING: '#28a745',   # 진행중 - 초록색
            ExhibitionStatus.ENDED: '#6c757d',     # 종료 - 회색
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 10px;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = '상태'

    def save_model(self, request, obj, form, change):
        """저장 전에 상태 자동 업데이트"""
        super().save_model(request, obj, form, change)


admin.site.register(ExhibitionLike)
