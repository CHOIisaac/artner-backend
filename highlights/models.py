from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel


class Highlight(TimeStampedModel):
    """하이라이트 모델"""
    ITEM_TYPES = (
        ('artist', _('작가')),
        ('artwork', _('작품')),
    )

    item_type = models.CharField(_('항목 유형'), max_length=10, choices=ITEM_TYPES)
    item_name = models.CharField(_('항목명'), max_length=200)
    item_info = models.CharField(_('항목 정보'), max_length=200, blank=True)

    # 하이라이트 내용
    highlighted_text = models.TextField(_('하이라이트된 텍스트'))

    # 메모 (선택 사항)
    note = models.TextField(_('메모'), blank=True)

    class Meta:
        verbose_name = _('하이라이트')
        verbose_name_plural = _('하이라이트 목록')
        ordering = ['-created_at']
        db_table = 'highlight'
        indexes = [
            models.Index(fields=['item_type', '-created_at']),
            models.Index(fields=['item_type', 'created_at']),  # 타입별 오래된순 조회 최적화
            models.Index(fields=['item_name']),  # item_name 단일 인덱스
        ]

    def __str__(self):
        return f"{self.item_name} - {self.highlighted_text[:30]}..."