from django.db import transaction
from django.shortcuts import get_object_or_404
from .repositories import ArtistLikeRepository
from .models import Artist


class ArtistService:
    """작가 서비스 - 좋아요 기능만"""
    
    def __init__(self):
        self.like_repo = ArtistLikeRepository()
    
    @transaction.atomic
    def toggle_like(self, user_id: int, artist_id: int) -> dict:
        """작가 좋아요 토글"""
        # 작가 존재 확인
        artist = get_object_or_404(Artist, id=artist_id)
        
        # 좋아요 상태 확인
        is_liked = self.like_repo.is_liked_by_user(user_id, artist_id)
        
        if is_liked:
            # 좋아요 제거
            self.like_repo.remove_like(user_id, artist_id)
            artist.likes_count = max(0, artist.likes_count - 1)
            artist.save()
            liked = False
        else:
            # 좋아요 추가
            self.like_repo.create_like(user_id, artist_id)
            artist.likes_count += 1
            artist.save()
            liked = True
        
        return {
            'liked': liked,
            'likes_count': artist.likes_count
        }
    
    def get_like_status(self, user_id: int, artist_id: int) -> dict:
        """작가 좋아요 상태 조회"""
        # 작가 존재 확인
        artist = get_object_or_404(Artist, id=artist_id)
        
        is_liked = self.like_repo.is_liked_by_user(user_id, artist_id)
        
        return {
            'liked': is_liked,
            'likes_count': artist.likes_count
        } 