from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModel


class ExhibitionRecord(TimeStampedModel):
    """전시 관람 기록 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exhibition_records',
        verbose_name=_('사용자')
    )
    visit_date = models.DateField(_('관람일'))
    name = models.CharField(_('전시명'), max_length=200)
    museum = models.CharField(_('미술관/갤러리'), max_length=100)
    note = models.TextField(_('메모'), blank=True)
    image = models.ImageField(_('이미지'), upload_to='records/images/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('전시 관람 기록')
        verbose_name_plural = _('전시 관람 기록 목록')
        db_table = 'exhibition_record'
        indexes = [
            models.Index(fields=['user', '-visit_date']),  # 사용자별 최신 관람일순 최적화
            models.Index(fields=['-created_at']),  # 기록 생성일순 최적화
            models.Index(fields=['visit_date']),  # 관람일 정렬 최적화
            models.Index(fields=['museum']),  # 미술관별 검색 최적화
            models.Index(fields=['user', '-created_at']),  # 사용자별 최신 기록순 최적화
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.visit_date})"
