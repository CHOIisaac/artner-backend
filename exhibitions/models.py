from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel, NamedModel

# Create your models here.

class ExhibitionStatus(models.TextChoices):
    UPCOMING = 'upcoming', _('예정')
    ONGOING = 'ongoing', _('진행중')
    ENDED = 'ended', _('종료')

class Exhibition(NamedModel):
    """전시 모델"""
    venue = models.CharField(_('장소'), max_length=100)
    start_date = models.DateField(_('시작일'))
    end_date = models.DateField(_('종료일'))
    poster_image = models.ImageField(_('포스터 이미지'), upload_to='exhibitions/posters/', blank=True, null=True)
    thumbnail_image = models.ImageField(_('썸네일 이미지'), upload_to='exhibitions/thumbnails/', blank=True, null=True)
    status = models.CharField(
        _('상태'),
        max_length=10,
        choices=ExhibitionStatus.choices,
        default=ExhibitionStatus.UPCOMING
    )
    is_featured = models.BooleanField(_('주요 전시 여부'), default=False)
    admission_fee = models.CharField(_('입장료'), max_length=100, blank=True)
    website = models.URLField(_('웹사이트'), blank=True)
    
    class Meta:
        verbose_name = _('전시')
        verbose_name_plural = _('전시 목록')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """전시 상태 자동 업데이트"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if today < self.start_date:
            self.status = ExhibitionStatus.UPCOMING
        elif self.start_date <= today <= self.end_date:
            self.status = ExhibitionStatus.ONGOING
        else:
            self.status = ExhibitionStatus.ENDED
            
        super().save(*args, **kwargs)

class ExhibitionDetail(TimeStampedModel):
    """전시 상세 정보 모델"""
    exhibition = models.OneToOneField(
        Exhibition, 
        on_delete=models.CASCADE, 
        related_name='detail',
        verbose_name=_('전시')
    )
    curator = models.CharField(_('큐레이터'), max_length=100, blank=True)
    opening_hours = models.CharField(_('관람 시간'), max_length=100, blank=True)
    gallery_map = models.ImageField(_('전시장 지도'), upload_to='exhibitions/maps/', blank=True, null=True)
    additional_images = models.JSONField(_('추가 이미지'), default=list, blank=True)
    related_events = models.JSONField(_('관련 이벤트'), default=list, blank=True)
    
    class Meta:
        verbose_name = _('전시 상세 정보')
        verbose_name_plural = _('전시 상세 정보 목록')
    
    def __str__(self):
        return f"{self.exhibition.title} 상세 정보"
