from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel
from users.models import User
from exhibitions.models import Exhibition
from artworks.models import Artwork

class DocentType(models.TextChoices):
    PERSONAL = 'personal', _('개인 도슨트')
    OFFICIAL = 'official', _('공식 도슨트')
    CURATOR = 'curator', _('큐레이터 도슨트')
    AI = 'ai', _('AI 도슨트')

class Docent(TimeStampedModel):
    """도슨트 모델"""
    title = models.CharField(_('제목'), max_length=200)
    description = models.TextField(_('설명'), blank=True)
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='docents',
        verbose_name=_('작성자')
    )
    exhibition = models.ForeignKey(
        Exhibition, 
        on_delete=models.CASCADE, 
        related_name='docents',
        verbose_name=_('전시')
    )
    type = models.CharField(
        _('도슨트 유형'),
        max_length=10,
        choices=DocentType.choices,
        default=DocentType.PERSONAL
    )
    is_public = models.BooleanField(_('공개 여부'), default=True)
    thumbnail_image = models.ImageField(_('썸네일 이미지'), upload_to='docents/thumbnails/', blank=True, null=True)
    duration = models.PositiveIntegerField(_('소요 시간(분)'), default=30)
    view_count = models.PositiveIntegerField(_('조회수'), default=0)
    like_count = models.PositiveIntegerField(_('좋아요 수'), default=0)
    
    class Meta:
        verbose_name = _('도슨트')
        verbose_name_plural = _('도슨트 목록')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class DocentItem(TimeStampedModel):
    """도슨트 항목 모델"""
    docent = models.ForeignKey(
        Docent, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_('도슨트')
    )
    artwork = models.ForeignKey(
        Artwork, 
        on_delete=models.CASCADE, 
        related_name='docent_items',
        verbose_name=_('작품')
    )
    order = models.PositiveIntegerField(_('순서'))
    commentary = models.TextField(_('해설'))
    audio = models.FileField(_('오디오 파일'), upload_to='docents/audio/', blank=True, null=True)
    duration = models.PositiveIntegerField(_('오디오 길이(초)'), default=0)
    
    class Meta:
        verbose_name = _('도슨트 항목')
        verbose_name_plural = _('도슨트 항목 목록')
        ordering = ['docent', 'order']
        unique_together = ['docent', 'order']
    
    def __str__(self):
        return f"{self.docent.title} - {self.artwork.title} ({self.order}번)"
