from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    """사용자 모델"""
    nickname = models.CharField(max_length=50, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    preferences = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    class Meta:
        db_table = 'art_users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'
    
    def __str__(self):
        return self.nickname or self.username 