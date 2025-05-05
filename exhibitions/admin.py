from django.contrib import admin
from django.utils.html import format_html
from .models import Exhibition, ExhibitionStatus


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'venue', 'date_range', 'status_display', 'is_featured', 'preview_image']
    list_filter = ['status', 'is_featured']
    search_fields = ['title', 'venue', 'description']
    readonly_fields = ['status', 'preview_poster', 'preview_thumbnail']
    inlines = [ExhibitionDetailInline]

    fieldsets = [
        (None, {'fields': ['title', 'description']}),
        ('장소 및 일정', {'fields': ['venue', 'start_date', 'end_date', 'status']}),
        ('추가 정보', {'fields': ['admission_fee', 'website']}),
        ('특성', {'fields': ['is_featured', 'featured_order']}),
        ('포스터', {'fields': ['poster_image', 'preview_poster']}),
        ('썸네일', {'fields': ['thumbnail_image', 'preview_thumbnail']}),
    ]

    def preview_image(self, obj):
        if obj.thumbnail_image:
            return format_html('<img src="{}" width="80" />', obj.thumbnail_image.url)
        elif obj.poster_image:
            return format_html('<img src="{}" width="80" />', obj.poster_image.url)
        return "이미지 없음"
    preview_image.short_description = '이미지'

    def preview_poster(self, obj):
        if obj.poster_image:
            return format_html('<img src="{}" width="200" />', obj.poster_image.url)
        return "포스터 이미지 없음"
    preview_poster.short_description = '포스터 미리보기'

    def preview_thumbnail(self, obj):
        if obj.thumbnail_image:
            return format_html('<img src="{}" width="150" />', obj.thumbnail_image.url)
        return "썸네일 이미지 없음"
    preview_thumbnail.short_description = '썸네일 미리보기'

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
        # save 메서드에서 자동으로 처리되므로 그대로 진행
        super().save_model(request, obj, form, change)
