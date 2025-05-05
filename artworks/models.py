from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel, NamedModel, FeaturedModel
from exhibitions.models import Exhibition


# Create your models here.
class Artwork(NamedModel, TimeStampedModel):
    """작품 모델"""
    title = models.CharField(_('작품명'), max_length=200)
    image = models.ImageField(_('작품 이미지'), upload_to='artworks/images/', blank=True, null=True)
    artist_name = models.CharField(_('작가명'), max_length=100)
    created_year = models.CharField(_('제작년도'), max_length=10, blank=True)
    description = models.TextField(_('설명'), blank=True)
    exhibition = models.ForeignKey(
        Exhibition, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='artworks',
        verbose_name=_('전시')
    )
    
    class Meta:
        verbose_name = _('작품')
        verbose_name_plural = _('작품 목록')
        ordering = ['artist_name', 'title']
    
    def __str__(self):
        return f"{self.title} - {self.artist_name}"
