from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel, NamedModel, PublishableModel
from users.models import User
from exhibitions.models import Exhibition
from artworks.models import Artwork
from artists.models import Artist
from django.conf import settings


class DocentScript(TimeStampedModel):
    """도슨트 스크립트 모델"""
    ITEM_TYPES = (
        ('artist', _('작가')),
        ('artwork', _('작품')),
    )

    item_type = models.CharField(_('항목 유형'), max_length=10, choices=ITEM_TYPES)
    item_name = models.CharField(_('항목명'), max_length=200)
    item_info = models.CharField(_('항목 정보'), max_length=200, blank=True)
    
    # 프롬프트 및 응답
    prompt_text = models.TextField(_('프롬프트 텍스트'))
    prompt_image = models.URLField(_('프롬프트 이미지 URL'), blank=True)
    llm_response = models.TextField(_('LLM 응답'))
    
    # 음성 파일
    openai_audio = models.FileField(_('OpenAI 음성'), upload_to='docents/openai_audio/', null=True, blank=True)
    polly_audio = models.FileField(_('Polly 음성'), upload_to='docents/polly_audio/', null=True, blank=True)
    timestamps = models.JSONField(_('타임스탬프'), null=True, blank=True)

    class Meta:
        verbose_name = _('도슨트 스크립트')
        verbose_name_plural = _('도슨트 스크립트 목록')
        ordering = ['-created_at']
        db_table = 'docent_script'
        indexes = [
            models.Index(fields=['item_type', '-created_at']),
            models.Index(fields=['item_name']),
        ]

    def __str__(self):
        return f"{self.item_name} ({self.get_item_type_display()}) - {self.created_at}"


class Folder(TimeStampedModel):
    """저장 폴더 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='save_folders',
        verbose_name=_('사용자')
    )
    name = models.CharField(_('폴더명'), max_length=100)
    description = models.TextField(_('설명'), blank=True)

    class Meta:
        verbose_name = _('저장 폴더')
        verbose_name_plural = _('저장 폴더 목록')
        unique_together = ('user', 'name')
        ordering = ['name']
        db_table = 'save_folder'
        indexes = [
            models.Index(fields=['user', 'name']),  # 사용자별 폴더명 정렬 최적화
            models.Index(fields=['user', '-created_at']),  # 사용자별 최신순 최적화
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class FolderItem(TimeStampedModel):
    """저장된 항목 모델"""
    ITEM_TYPES = (
        ('artist', _('작가')),
        ('artwork', _('작품')),
    )

    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('폴더')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_items',
        verbose_name=_('사용자')
    )
    item_type = models.CharField(_('항목 유형'), max_length=10, choices=ITEM_TYPES)

    # 공통 필드
    title = models.CharField(_('제목'), max_length=200)

    # 작가 전용 필드
    life_period = models.CharField(_('생애기간'), max_length=50, blank=True)  # 작가일 경우 출생-사망

    # 작품 전용 필드
    artist_name = models.CharField(_('작가명'), max_length=100, blank=True)

    # 기타 정보
    notes = models.TextField(_('메모'), blank=True)
    thumbnail = models.ImageField(_('썸네일'), upload_to='saved_items/thumbnails/', null=True, blank=True)

    class Meta:
        verbose_name = _('저장 항목')
        verbose_name_plural = _('저장 항목 목록')
        unique_together = ('folder', 'item_type', 'title')
        ordering = ['-created_at']
        db_table = 'saved_item'
        indexes = [
            models.Index(fields=['item_type', 'created_at']),
            models.Index(fields=['user', 'item_type']),
            models.Index(fields=['user', '-created_at']),  # 사용자별 최신순 최적화
            models.Index(fields=['folder', 'item_type']),  # 폴더별 타입 필터링 최적화
            models.Index(fields=['title']),  # title 단일 인덱스
            models.Index(fields=['artist_name']),  # artist_name 단일 인덱스
        ]

    def __str__(self):
        if self.item_type == 'artist':
            return f"{self.folder.name} - {self.title} (작가)"
        else:
            return f"{self.folder.name} - {self.title} (작품)"
