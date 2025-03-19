from django.db import models


class Museum(models.Model):
    """미술관 모델"""
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='museums/', null=True, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'museums'
        verbose_name = '미술관'
        verbose_name_plural = '미술관 목록'
        indexes = [models.Index(fields=['name'])]
    
    def __str__(self):
        return self.name 