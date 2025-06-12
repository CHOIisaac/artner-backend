from django.db import transaction
from django.shortcuts import get_object_or_404
from .repositories import ExhibitionLikeRepository
from .models import Exhibition


class ExhibitionService:
    """전시회 서비스 - 좋아요 기능만"""
    
    def __init__(self):
        self.like_repo = ExhibitionLikeRepository()
    
    @transaction.atomic
    def toggle_like(self, user_id: int, exhibition_id: int) -> dict:
        """전시회 좋아요 토글"""
        # 전시회 존재 확인
        exhibition = get_object_or_404(Exhibition, id=exhibition_id)
        
        # 좋아요 상태 확인
        is_liked = self.like_repo.is_liked_by_user(user_id, exhibition_id)
        
        if is_liked:
            # 좋아요 제거
            self.like_repo.remove_like(user_id, exhibition_id)
            exhibition.likes_count = max(0, exhibition.likes_count - 1)
            exhibition.save()
            liked = False
        else:
            # 좋아요 추가
            self.like_repo.create_like(user_id, exhibition_id)
            exhibition.likes_count += 1
            exhibition.save()
            liked = True
        
        return {
            'liked': liked,
            'likes_count': exhibition.likes_count
        }
    
    def get_like_status(self, user_id: int, exhibition_id: int) -> dict:
        """전시회 좋아요 상태 조회"""
        # 전시회 존재 확인
        exhibition = get_object_or_404(Exhibition, id=exhibition_id)
        
        is_liked = self.like_repo.is_liked_by_user(user_id, exhibition_id)
        
        return {
            'liked': is_liked,
            'likes_count': exhibition.likes_count
        } 