from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModel, NamedModel
import random


class ArtistManager(models.Manager):
    """Artist 모델을 위한 커스텀 매니저"""
    
    def random(self, count=4):
        """효율적인 랜덤 조회"""
        # ID 범위 구하기
        min_id = self.aggregate(models.Min('id'))['id__min']
        max_id = self.aggregate(models.Max('id'))['id__max']
        
        if min_id is None or max_id is None:
            return self.none()
        
        # 랜덤 ID 생성
        random_ids = []
        attempts = 0
        while len(random_ids) < count and attempts < count * 3:  # 최대 시도 제한
            random_id = random.randint(min_id, max_id)
            if random_id not in random_ids:
                random_ids.append(random_id)
            attempts += 1
        
        # ID가 존재하는 객체들만 반환
        return self.filter(id__in=random_ids)[:count]


class Artist(NamedModel, TimeStampedModel):
    """작가 모델"""
    # NamedModel에서 title, description 상속받음 (title=작가명, description=작가소개)
    life_period = models.CharField(_('출생-사망'), max_length=50, blank=True, help_text=_('예: 1853-1890, 1967-현재'))
    representative_work = models.CharField(_('대표작'), max_length=200, blank=True)
    image = models.ImageField(_('작가 이미지'), upload_to='artists/images/', blank=True, null=True)
    likes_count = models.PositiveIntegerField(_('좋아요 수'), default=0)

    objects = ArtistManager()  # 커스텀 매니저 설정

    class Meta:
        verbose_name = _('작가')
        verbose_name_plural = _('작가 목록')
        ordering = ['title']  # name -> title로 변경
        db_table = 'artist'
        indexes = [
            models.Index(fields=['title']),  # 이름 정렬 최적화
            models.Index(fields=['-likes_count']),  # 좋아요순 정렬 최적화
            models.Index(fields=['-created_at']),  # 최신순 정렬 최적화
            models.Index(fields=['id']),  # 랜덤 조회 최적화 (Primary Key라서 자동이지만 명시)
        ]

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