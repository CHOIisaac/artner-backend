from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel, NamedModel, PublishableModel
from users.models import User
from exhibitions.models import Exhibition
from artworks.models import Artwork
from artists.models import Artist
from django.conf import settings


class SaveFolder(TimeStampedModel):
    """저장 폴더 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='save_folders',
        verbose_name=_('사용자')
    )
    name = models.CharField(_('폴더명'), max_length=100)
    description = models.TextField(_('설명'), blank=True)

    class Meta:
        verbose_name = _('저장 폴더')
        verbose_name_plural = _('저장 폴더 목록')
        unique_together = ('user', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class SavedItem(TimeStampedModel):
    """저장된 항목 모델"""
    ITEM_TYPES = (
        ('artist', _('작가')),
        ('artwork', _('작품')),
    )

    folder = models.ForeignKey(
        SaveFolder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('폴더')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_items',
        verbose_name=_('사용자')
    )
    item_type = models.CharField(_('항목 유형'), max_length=10, choices=ITEM_TYPES, db_index=True)

    # 공통 필드
    title = models.CharField(_('제목'), max_length=200, db_index=True)  # 작가명 또는 작품명

    # 작가 전용 필드
    life_period = models.CharField(_('생애기간'), max_length=50, blank=True)  # 작가일 경우 출생-사망

    # 작품 전용 필드
    artist_name = models.CharField(_('작가명'), max_length=100, blank=True, db_index=True)  # 작품일 경우 작가명

    # 기타 정보
    notes = models.TextField(_('메모'), blank=True)
    thumbnail = models.ImageField(_('썸네일'), upload_to='saved_items/thumbnails/', null=True, blank=True)

    class Meta:
        verbose_name = _('저장 항목')
        verbose_name_plural = _('저장 항목 목록')
        unique_together = ('folder', 'item_type', 'title')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item_type', 'created_at']),
            models.Index(fields=['user', 'item_type']),
        ]

    def __str__(self):
        if self.item_type == 'artist':
            return f"{self.folder.name} - {self.title} (작가)"
        else:
            return f"{self.folder.name} - {self.title} (작품)"
