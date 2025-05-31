from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Highlight(models.Model):
    """
    작품이나 전시회의 하이라이트 정보를 저장하는 모델
    """
    title = models.CharField(max_length=100, verbose_name='하이라이트 제목')
    description = models.TextField(verbose_name='하이라이트 설명')
    
    # 하이라이트 타입 (작품 또는 전시회)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 하이라이트 표시 순서
    order = models.PositiveIntegerField(default=0, verbose_name='표시 순서')
    
    # 하이라이트 상태
    is_active = models.BooleanField(default=True, verbose_name='활성화 상태')
    
    # 생성 및 수정 시간
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = '하이라이트'
        verbose_name_verbose_name_plural = '하이라이트'
        
    def __str__(self):
        return self.title
