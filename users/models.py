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
        db_table = 'user'
    
    def __str__(self):
        return self.username
