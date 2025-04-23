from django.db import models

# 필요한 경우 로깅 목적으로만 사용
class ChatLog(models.Model):
    """채팅 로그 (선택적 사용)"""
    query = models.TextField(verbose_name='질문')
    response = models.TextField(verbose_name='응답')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at'] 