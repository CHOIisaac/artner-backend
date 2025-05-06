from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModel, NamedModel


# Create your models here.
class Artwork(NamedModel, TimeStampedModel):
    """작품 모델"""
    title = models.CharField(_('작품명'), max_length=200)
    image = models.ImageField(_('작품 이미지'), upload_to='artworks/images/', blank=True, null=True)
    artist_name = models.CharField(_('작가명'), max_length=100)
    created_year = models.CharField(_('제작년도'), max_length=10, blank=True)
    description = models.TextField(_('설명'), blank=True)
    likes_count = models.PositiveIntegerField(_('좋아요 수'), default=0)
    
    class Meta:
        verbose_name = _('작품')
        verbose_name_plural = _('작품 목록')
        ordering = ['artist_name', 'title']
        db_table = 'Artwork'
    
    def __str__(self):
        return f"{self.title} - {self.artist_name}"


class ArtworkLike(TimeStampedModel):
    """작품 좋아요 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='liked_artworks',
        verbose_name=_('사용자')
    )
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('작품')
    )
    
    class Meta:
        verbose_name = _('작품 좋아요')
        verbose_name_plural = _('작품 좋아요 목록')
        unique_together = ('user', 'artwork')
        db_table = 'ArtworkLike'
        
    def __str__(self):
        return f"{self.user.username} - {self.artwork.title}"
