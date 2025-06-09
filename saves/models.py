from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModel
from artists.models import Artist
from artworks.models import Artwork
from exhibitions.models import Exhibition


class SaveFolder(TimeStampedModel):
    """사용자의 저장 폴더 모델"""
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
        unique_together = ('user', 'name')  # 사용자별로 폴더명 중복 방지
        db_table = 'SaveFolder'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class SaveItem(TimeStampedModel):
    """저장된 항목 모델"""
    ITEM_TYPES = (
        ('artist', _('작가')),
        ('artwork', _('작품')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='saved_items',
        verbose_name=_('사용자')
    )
    folder = models.ForeignKey(
        SaveFolder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('저장 폴더')
    )
    item_type = models.CharField(_('항목 유형'), max_length=20, choices=ITEM_TYPES)
    
    # 항목 ID (각 항목 타입에 맞는 외래 키 대신 ID만 저장)
    item_id = models.PositiveIntegerField(_('항목 ID'))
    
    # 선택적 메모
    notes = models.TextField(_('메모'), blank=True)
    
    class Meta:
        verbose_name = _('저장 항목')
        verbose_name_plural = _('저장 항목 목록')
        unique_together = ('user', 'folder', 'item_type', 'item_id')  # 폴더 내 중복 저장 방지
        db_table = 'SaveItem'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.folder.name} - {self.item_type} #{self.item_id}"
    
    @property
    def item(self):
        """저장된 실제 항목(작가, 작품, 전시회) 객체를 반환"""
        if self.item_type == 'artist':
            return Artist.objects.filter(id=self.item_id).first()
        elif self.item_type == 'artwork':
            return Artwork.objects.filter(id=self.item_id).first()
        elif self.item_type == 'exhibition':
            return Exhibition.objects.filter(id=self.item_id).first()
        return None
