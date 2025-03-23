from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel
from exhibitions.models import Exhibition

# Create your models here.

class ArtworkType(models.TextChoices):
    PAINTING = 'painting', _('회화')
    SCULPTURE = 'sculpture', _('조각')
    INSTALLATION = 'installation', _('설치미술')
    PHOTOGRAPHY = 'photography', _('사진')
    MEDIA_ART = 'media_art', _('미디어아트')
    CRAFT = 'craft', _('공예')
    DRAWING = 'drawing', _('드로잉')
    PRINT = 'print', _('판화')
    PERFORMANCE = 'performance', _('퍼포먼스')
    OTHER = 'other', _('기타')

class Artwork(TimeStampedModel):
    """작품 모델"""
    title = models.CharField(_('제목'), max_length=200)
    artist = models.CharField(_('작가'), max_length=100)
    year = models.CharField(_('제작연도'), max_length=20, blank=True)
    description = models.TextField(_('설명'), blank=True)
    image = models.ImageField(_('이미지'), upload_to='artworks/', blank=True, null=True)
    type = models.CharField(_('작품 유형'), max_length=20, choices=ArtworkType.choices, default=ArtworkType.PAINTING)
    medium = models.CharField(_('재료'), max_length=200, blank=True)
    dimensions = models.CharField(_('크기'), max_length=100, blank=True)
    exhibition = models.ForeignKey(
        Exhibition, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='artworks',
        verbose_name=_('전시')
    )
    is_featured = models.BooleanField(_('주요 작품 여부'), default=False)
    
    class Meta:
        verbose_name = _('작품')
        verbose_name_plural = _('작품 목록')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.artist}"

class ArtworkDetail(TimeStampedModel):
    """작품 상세 정보 모델"""
    artwork = models.OneToOneField(
        Artwork, 
        on_delete=models.CASCADE, 
        related_name='detail',
        verbose_name=_('작품')
    )
    historical_context = models.TextField(_('역사적 맥락'), blank=True)
    technique_details = models.TextField(_('기법 상세'), blank=True)
    symbolism = models.TextField(_('상징성'), blank=True)
    provenance = models.TextField(_('출처/소장 이력'), blank=True)
    additional_images = models.JSONField(_('추가 이미지'), default=list, blank=True)
    references = models.JSONField(_('참고 자료'), default=list, blank=True)
    
    class Meta:
        verbose_name = _('작품 상세 정보')
        verbose_name_plural = _('작품 상세 정보 목록')
    
    def __str__(self):
        return f"{self.artwork.title} 상세 정보"
