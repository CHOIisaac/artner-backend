from django.db import models

from .user import User


class Like(models.Model):
    """좋아요 모델"""
    CONTENT_TYPES = (
        ('exhibition', '전시'),
        ('artwork', '작품'),
        ('docent', '도슨트'),
        ('highlight', '하이라이트'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes'
        verbose_name = '좋아요'
        verbose_name_plural = '좋아요 목록'
        unique_together = ('user', 'content_type', 'object_id')
    
    def __str__(self):
        return f"{self.user.username}의 {self.get_content_type_display()} 좋아요" 