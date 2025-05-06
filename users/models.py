from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class User(AbstractUser):
    """사용자 모델"""
    nickname = models.CharField(
        _('닉네임'), 
        max_length=50, 
        blank=True,
        help_text=_('사용자의 표시 이름입니다.')
    )
    profile_image = models.ImageField(
        _('프로필 이미지'), 
        upload_to='users/profiles/', 
        null=True, 
        blank=True,
        help_text=_('사용자의 프로필 이미지입니다.')
    )
    bio = models.TextField(_('자기소개'), blank=True)
    preferences = ArrayField(
        models.CharField(max_length=50),
        verbose_name=_('선호 장르'),
        blank=True,
        default=list
    )
    
    class Meta:
        verbose_name = _('사용자')
        verbose_name_plural = _('사용자 목록')
        db_table = 'User'
    
    def __str__(self):
        return self.username

class UserPreference(models.Model):
    """사용자 취향 모델"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='preference_detail',
        verbose_name=_('사용자')
    )
    favorite_artists = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_('선호 작가'),
        blank=True,
        default=list
    )
    favorite_genres = ArrayField(
        models.CharField(max_length=50),
        verbose_name=_('선호 장르'),
        blank=True,
        default=list
    )
    favorite_periods = ArrayField(
        models.CharField(max_length=50),
        verbose_name=_('선호 시대'),
        blank=True,
        default=list
    )
    visit_frequency = models.CharField(_('방문 빈도'), max_length=20, blank=True)
    
    class Meta:
        verbose_name = _('사용자 취향')
        verbose_name_plural = _('사용자 취향 목록')
    
    def __str__(self):
        return f"{self.user.username}의 취향"
