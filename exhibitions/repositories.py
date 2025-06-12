from .models import ExhibitionLike


class ExhibitionLikeRepository:
    """전시회 좋아요 레포지토리"""
    
    def create_like(self, user_id: int, exhibition_id: int) -> ExhibitionLike:
        """좋아요 생성"""
        return ExhibitionLike.objects.create(
            user_id=user_id,
            exhibition_id=exhibition_id
        )
    
    def remove_like(self, user_id: int, exhibition_id: int) -> bool:
        """좋아요 제거"""
        try:
            like = ExhibitionLike.objects.get(
                user_id=user_id,
                exhibition_id=exhibition_id
            )
            like.delete()
            return True
        except ExhibitionLike.DoesNotExist:
            return False
    
    def is_liked_by_user(self, user_id: int, exhibition_id: int) -> bool:
        """사용자가 좋아요했는지 확인"""
        return ExhibitionLike.objects.filter(
            user_id=user_id,
            exhibition_id=exhibition_id
        ).exists() 