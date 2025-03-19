from django.db import models

from .user import User


class Collection(models.Model):
    """사용자 컬렉션 모델"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collections'
        verbose_name = '컬렉션'
        verbose_name_plural = '컬렉션 목록'
    
    def __str__(self):
        return f"{self.user.username}의 {self.name}"


class CollectionItem(models.Model):
    """컬렉션 아이템 모델"""
    ITEM_TYPES = (
        ('exhibition', '전시'),
        ('artwork', '작품'),
        ('docent', '도슨트'),
    )
    
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    object_id = models.IntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'collection_items'
        verbose_name = '컬렉션 아이템'
        verbose_name_plural = '컬렉션 아이템 목록'
        unique_together = ('collection', 'item_type', 'object_id')
    
    def __str__(self):
        return f"{self.collection.name}의 {self.get_item_type_display()}" 