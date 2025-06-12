from .models import ArtistLike


class ArtistLikeRepository:
    """작가 좋아요 레포지토리"""
    
    def create_like(self, user_id: int, artist_id: int) -> ArtistLike:
        """좋아요 생성"""
        return ArtistLike.objects.create(
            user_id=user_id,
            artist_id=artist_id
        )
    
    def remove_like(self, user_id: int, artist_id: int) -> bool:
        """좋아요 제거"""
        try:
            like = ArtistLike.objects.get(
                user_id=user_id,
                artist_id=artist_id
            )
            like.delete()
            return True
        except ArtistLike.DoesNotExist:
            return False
    
    def is_liked_by_user(self, user_id: int, artist_id: int) -> bool:
        """사용자가 좋아요했는지 확인"""
        return ArtistLike.objects.filter(
            user_id=user_id,
            artist_id=artist_id
        ).exists() 