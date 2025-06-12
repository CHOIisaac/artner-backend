from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModel, NamedModel

# Create your models here.


class ExhibitionStatus(models.TextChoices):
    UPCOMING = 'upcoming', _('예정')
    ONGOING = 'ongoing', _('진행중')
    ENDED = 'ended', _('종료')


class Exhibition(NamedModel, TimeStampedModel):
    """전시 모델"""
    venue = models.CharField(_('장소'), max_length=100)
    start_date = models.DateField(_('시작일'))
    end_date = models.DateField(_('종료일'))
    status = models.CharField(
        _('상태'),
        max_length=10,
        choices=ExhibitionStatus.choices,
        default=ExhibitionStatus.UPCOMING
    )
    image = models.ImageField(_('전시 이미지'), upload_to='exhibitions/images/', blank=True, null=True)
    map_url = models.URLField(_('네이버 지도 링크'), blank=True)
    museum_url = models.URLField(_('미술관 링크'), blank=True)
    likes_count = models.PositiveIntegerField(_('좋아요 수'), default=0)
    
    class Meta:
        verbose_name = _('전시')
        verbose_name_plural = _('전시 목록')
        ordering = ['-start_date']
        db_table = 'exhibition'
    
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

    @property
    def likes_users(self):
        """이 전시를 좋아하는 사용자 목록 반환"""
        return [like.user for like in self.likes.all()]


class ExhibitionLike(TimeStampedModel):
    """전시 좋아요 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='liked_exhibitions',
        verbose_name=_('사용자')
    )
    exhibition = models.ForeignKey(
        Exhibition,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('전시')
    )
    
    class Meta:
        verbose_name = _('전시 좋아요')
        verbose_name_plural = _('전시 좋아요 목록')
        unique_together = ('user', 'exhibition')  # 사용자당 하나의 좋아요만 가능
        db_table = 'exhibition_like'
        
    def __str__(self):
        return f"{self.user.username} - {self.exhibition.title}"
