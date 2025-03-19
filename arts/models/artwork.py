from django.db import models
from django.contrib.postgres.search import SearchVectorField

from .artist import Artist
from .exhibition import Exhibition


class Artwork(models.Model):
    """작품 모델"""
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artworks')
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, related_name='artworks')
    year = models.IntegerField(null=True, blank=True)
    medium = models.CharField(max_length=100, blank=True)  # 재료
    dimensions = models.CharField(max_length=100, blank=True)  # 크기
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='artworks/', null=True, blank=True)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        db_table = 'artworks'
        verbose_name = '작품'
        verbose_name_plural = '작품 목록'
        indexes = [models.Index(fields=['title'])]
    
    def __str__(self):
        return f"{self.title} - {self.artist.name}" 