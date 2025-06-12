from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModel, NamedModel
import random


class ArtworkManager(models.Manager):
    """Artwork 모델을 위한 커스텀 매니저"""
    
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


# Create your models here.
class Artwork(NamedModel, TimeStampedModel):
    """작품 모델"""
    # NamedModel에서 title, description 상속받음 (title=작품명, description=작품설명)
    image = models.ImageField(_('작품 이미지'), upload_to='artworks/images/', blank=True, null=True)
    artist_name = models.CharField(_('작가명'), max_length=100)
    created_year = models.CharField(_('제작년도'), max_length=10, blank=True)
    likes_count = models.PositiveIntegerField(_('좋아요 수'), default=0)
    
    objects = ArtworkManager()  # 커스텀 매니저 설정
    
    class Meta:
        verbose_name = _('작품')
        verbose_name_plural = _('작품 목록')
        ordering = ['artist_name', 'title']
        db_table = 'artwork'
        indexes = [
            models.Index(fields=['artist_name', 'title']),  # 기본 정렬 최적화
            models.Index(fields=['artist_name']),  # 작가별 필터링 최적화
            models.Index(fields=['-likes_count']),  # 좋아요순 정렬 최적화
            models.Index(fields=['-created_at']),  # 최신순 정렬 최적화
            models.Index(fields=['created_year']),  # 제작년도별 검색 최적화
            models.Index(fields=['id']),  # 랜덤 조회 최적화 (Primary Key라서 자동이지만 명시)
        ]
    
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
        db_table = 'artwork_like'
        
    def __str__(self):
        return f"{self.user.username} - {self.artwork.title}"
