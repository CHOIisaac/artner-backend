from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModel, NamedModel, FeaturedModel


class Artist(NamedModel, TimeStampedModel):
    """작가 모델"""
    name = models.CharField(_('작가명'), max_length=100)
    life_period = models.CharField(_('출생-사망'), max_length=50, blank=True, help_text=_('예: 1853-1890, 1967-현재'))
    representative_work = models.CharField(_('대표작'), max_length=200, blank=True)
    image = models.ImageField(_('작가 이미지'), upload_to='artists/images/', blank=True, null=True)
    likes_count = models.PositiveIntegerField(_('좋아요 수'), default=0)

    class Meta:
        verbose_name = _('작가')
        verbose_name_plural = _('작가 목록')
        ordering = ['name']
        db_table = 'Artist'

    def __str__(self):
        return self.name


class ArtistLike(TimeStampedModel):
    """작가 좋아요 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='liked_artists',
        verbose_name=_('사용자')
    )
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('작가')
    )
    
    class Meta:
        verbose_name = _('작가 좋아요')
        verbose_name_plural = _('작가 좋아요 목록')
        unique_together = ('user', 'artist')
        db_table = 'ArtistLike'
        
    def __str__(self):
        return f"{self.user.username} - {self.artist.name}"