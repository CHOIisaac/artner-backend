from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModel, NamedModel


class Artist(NamedModel, TimeStampedModel):
    """작가 모델"""
    # NamedModel에서 title, description 상속받음 (title=작가명, description=작가소개)
    life_period = models.CharField(_('출생-사망'), max_length=50, blank=True, help_text=_('예: 1853-1890, 1967-현재'))
    representative_work = models.CharField(_('대표작'), max_length=200, blank=True)
    image = models.ImageField(_('작가 이미지'), upload_to='artists/images/', blank=True, null=True)
    likes_count = models.PositiveIntegerField(_('좋아요 수'), default=0)

    class Meta:
        verbose_name = _('작가')
        verbose_name_plural = _('작가 목록')
        ordering = ['title']  # name -> title로 변경
        db_table = 'artist'

    def __str__(self):
        return self.title  # name -> title로 변경
    
    @property 
    def name(self):
        """하위 호환성을 위한 name 프로퍼티"""
        return self.title


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
        db_table = 'artist_like'
        
    def __str__(self):
        return f"{self.user.username} - {self.artist.title}"  # name -> title