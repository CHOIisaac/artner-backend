from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.utils import timezone

from .museum import Museum


class Exhibition(models.Model):
    """전시 모델"""
    title = models.CharField(max_length=200)
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name='exhibitions')
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    poster = models.ImageField(upload_to='exhibitions/', null=True, blank=True)
    categories = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    is_public = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        db_table = 'exhibitions'
        verbose_name = '전시'
        verbose_name_plural = '전시 목록'
        indexes = [models.Index(fields=['title'])]
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date 