from django.db import models

from .user import User
from .exhibition import Exhibition
from .artwork import Artwork


class Docent(models.Model):
    """도슨트 모델"""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='docents')
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, related_name='docents')
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'docents'
        verbose_name = '도슨트'
        verbose_name_plural = '도슨트 목록'
    
    def __str__(self):
        return self.title


class Highlight(models.Model):
    """작품 하이라이트 모델"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highlights')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='highlights')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'highlights'
        verbose_name = '하이라이트'
        verbose_name_plural = '하이라이트 목록'
        unique_together = ('user', 'artwork')
    
    def __str__(self):
        return f"{self.user.username}의 {self.artwork.title} 하이라이트" 