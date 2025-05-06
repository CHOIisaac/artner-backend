from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel, NamedModel, PublishableModel
from users.models import User
from exhibitions.models import Exhibition
from artworks.models import Artwork
from django.conf import settings


class DocentType(models.TextChoices):
    PERSONAL = 'personal', _('개인 도슨트')
    OFFICIAL = 'official', _('공식 도슨트')
    CURATOR = 'curator', _('큐레이터 도슨트')
    AI = 'ai', _('AI 도슨트')


class Docent(NamedModel, PublishableModel):
    """도슨트 모델"""
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
    thumbnail_image = models.ImageField(_('썸네일 이미지'), upload_to='docents/thumbnails/', blank=True, null=True)
    audio_file = models.FileField(_('오디오 파일'), upload_to='docents/audio/', blank=True, null=True)
    duration = models.PositiveIntegerField(_('재생 시간(초)'), default=0)
    view_count = models.PositiveIntegerField(_('조회수'), default=0)
    like_count = models.PositiveIntegerField(_('좋아요 수'), default=0)
    
    class Meta:
        verbose_name = _('도슨트')
        verbose_name_plural = _('도슨트 목록')
        db_table = 'Docent'
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
    audio_file = models.FileField(upload_to='docent_audios/', null=True, blank=True, verbose_name='오디오 파일')
    duration = models.PositiveIntegerField(default=0, verbose_name='오디오 길이(초)')
    
    # def save(self, *args, **kwargs):
    #     # 오디오 파일이 있으면 길이 계산 (필요한 경우 라이브러리 설치 필요)
    #     if self.audio_file and not self.duration:
    #         try:
    #             from pydub import AudioSegment
    #             audio = AudioSegment.from_file(self.audio_file.path)
    #             self.duration = len(audio) // 1000  # milliseconds to seconds
    #         except:
    #             pass
    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('도슨트 항목')
        verbose_name_plural = _('도슨트 항목 목록')
        ordering = ['docent', 'order']
        unique_together = ['docent', 'order']
    
    def __str__(self):
        return f"{self.docent.title} - {self.artwork.title} ({self.order}번)"


class DocentHighlight(models.Model):
    """도슨트 텍스트 하이라이트 모델"""
    docent = models.ForeignKey(
        Docent, 
        on_delete=models.CASCADE, 
        related_name='highlights',
        verbose_name=_('도슨트')
    )
    docent_item = models.ForeignKey(
        DocentItem,
        on_delete=models.CASCADE,
        related_name='highlights',
        verbose_name=_('도슨트 항목'),
        null=True,
        blank=True
    )
    text = models.TextField(_('하이라이트 텍스트'))
    start_position = models.PositiveIntegerField(_('시작 위치'))
    end_position = models.PositiveIntegerField(_('종료 위치'))
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='docent_highlights',
        verbose_name=_('사용자')
    )
    note = models.TextField(_('메모'), blank=True)
    is_public = models.BooleanField(_('공개 여부'), default=False)
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    
    class Meta:
        verbose_name = _('도슨트 하이라이트')
        verbose_name_plural = _('도슨트 하이라이트 목록')
        ordering = ['start_position']
    
    def __str__(self):
        return f"{self.docent.title}의 하이라이트: {self.text[:20]}..."


class DocentLike(models.Model):
    """도슨트 좋아요 모델"""
    docent = models.ForeignKey('Docent', on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('docent', 'user')
