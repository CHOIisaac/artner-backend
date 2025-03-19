from django.db import models
from django.contrib.postgres.search import SearchVectorField


class Artist(models.Model):
    """아티스트 모델"""
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='artists/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        db_table = 'artists'
        verbose_name = '아티스트'
        verbose_name_plural = '아티스트 목록'
        indexes = [models.Index(fields=['name'])]
    
    def __str__(self):
        return self.name 