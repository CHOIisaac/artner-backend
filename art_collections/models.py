from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel, NamedModel, PublishableModel
from artworks.models import Artwork


class Collection(NamedModel, PublishableModel):
    """컬렉션 모델"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name=_('사용자')
    )
    thumbnail_image = models.ImageField(_('썸네일 이미지'), upload_to='collections/thumbnails/', blank=True, null=True)

    class Meta:
        verbose_name = _('컬렉션')
        verbose_name_plural = _('컬렉션 목록')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 {self.title}"


class CollectionItem(TimeStampedModel):
    """컬렉션 항목 모델"""
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('컬렉션')
    )
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name='collection_items',
        verbose_name=_('작품')
    )
    note = models.TextField(_('메모'), blank=True)
    order = models.PositiveIntegerField(_('순서'), default=0)

    class Meta:
        verbose_name = _('컬렉션 항목')
        verbose_name_plural = _('컬렉션 항목 목록')
        ordering = ['collection', 'order']
        unique_together = ['collection', 'artwork']

    def __str__(self):
        return f"{self.collection.title} - {self.artwork.title}"