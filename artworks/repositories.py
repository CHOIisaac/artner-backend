from .models import ArtworkLike


class ArtworkLikeRepository:
    """작품 좋아요 레포지토리"""
    
    def create_like(self, user_id: int, artwork_id: int) -> ArtworkLike:
        """좋아요 생성"""
        return ArtworkLike.objects.create(
            user_id=user_id,
            artwork_id=artwork_id
        )
    
    def remove_like(self, user_id: int, artwork_id: int) -> bool:
        """좋아요 제거"""
        try:
            like = ArtworkLike.objects.get(
                user_id=user_id,
                artwork_id=artwork_id
            )
            like.delete()
            return True
        except ArtworkLike.DoesNotExist:
            return False
    
    def is_liked_by_user(self, user_id: int, artwork_id: int) -> bool:
        """사용자가 좋아요했는지 확인"""
        return ArtworkLike.objects.filter(
            user_id=user_id,
            artwork_id=artwork_id
        ).exists() 