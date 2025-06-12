from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .models import Artwork, ArtworkLike
from .repositories import ArtworkLikeRepository
from .services import ArtworkService




class ArtworkLikeRepositoryTestCase(TestCase):
    """작품 좋아요 레포지토리 테스트"""
    
    def setUp(self):
        self.repository = ArtworkLikeRepository()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.artwork = Artwork.objects.create(
            title="Test Artwork",
            artist_name="Test Artist",
            description="Test Description",
            created_year="2024"
        )
    
    def test_create_like(self):
        """좋아요 생성 테스트"""
        like = self.repository.create_like(self.user.id, self.artwork.id)
        
        self.assertIsNotNone(like)
        self.assertEqual(like.user_id, self.user.id)
        self.assertEqual(like.artwork_id, self.artwork.id)
    
    def test_is_liked_by_user(self):
        """사용자 좋아요 여부 확인 테스트"""
        # 좋아요 하지 않은 상태
        self.assertFalse(
            self.repository.is_liked_by_user(self.user.id, self.artwork.id)
        )
        
        # 좋아요 한 후
        self.repository.create_like(self.user.id, self.artwork.id)
        self.assertTrue(
            self.repository.is_liked_by_user(self.user.id, self.artwork.id)
        )
    
    def test_remove_like(self):
        """좋아요 제거 테스트"""
        # 좋아요 생성
        self.repository.create_like(self.user.id, self.artwork.id)
        
        # 좋아요 제거
        result = self.repository.remove_like(self.user.id, self.artwork.id)
        self.assertTrue(result)
        
        # 제거 확인
        self.assertFalse(
            self.repository.is_liked_by_user(self.user.id, self.artwork.id)
        )


class ArtworkServiceTestCase(TestCase):
    """작품 서비스 테스트"""
    
    def setUp(self):
        self.service = ArtworkService()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.artwork = Artwork.objects.create(
            title="Test Artwork",
            artist_name="Test Artist",
            description="Test Description",
            created_year="2024"
        )
    
    def test_toggle_like_create(self):
        """좋아요 토글 - 생성"""
        result = self.service.toggle_like(self.user.id, self.artwork.id)
        
        self.assertTrue(result['liked'])
        self.assertTrue(
            ArtworkLike.objects.filter(
                user_id=self.user.id,
                artwork_id=self.artwork.id
            ).exists()
        )
    
    def test_toggle_like_remove(self):
        """좋아요 토글 - 제거"""
        # 먼저 좋아요 생성
        ArtworkLike.objects.create(
            user_id=self.user.id,
            artwork_id=self.artwork.id
        )
        
        # 토글로 제거
        result = self.service.toggle_like(self.user.id, self.artwork.id)
        
        self.assertFalse(result['liked'])
        self.assertFalse(
            ArtworkLike.objects.filter(
                user_id=self.user.id,
                artwork_id=self.artwork.id
            ).exists()
        )
    
    def test_get_like_status(self):
        """좋아요 상태 조회 테스트"""
        # 좋아요 하지 않은 상태
        status = self.service.get_like_status(self.user.id, self.artwork.id)
        self.assertFalse(status['liked'])
        
        # 좋아요 한 후
        ArtworkLike.objects.create(
            user_id=self.user.id,
            artwork_id=self.artwork.id
        )
        status = self.service.get_like_status(self.user.id, self.artwork.id)
        self.assertTrue(status['liked'])


class ArtworkAPITestCase(TestCase):
    """작품 API 테스트"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.artwork = Artwork.objects.create(
            title="Test Artwork",
            artist_name="Test Artist",
            description="Test Description",
            created_year="2024"
        )
    
    def test_toggle_like_unauthorized(self):
        """인증되지 않은 사용자의 좋아요 토글 요청"""
        url = reverse('artwork-toggle-like', kwargs={'artwork_id': self.artwork.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_toggle_like_authorized(self):
        """인증된 사용자의 좋아요 토글"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('artwork-toggle-like', kwargs={'artwork_id': self.artwork.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
    
    def test_like_status(self):
        """좋아요 상태 조회"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('artwork-like-status', kwargs={'artwork_id': self.artwork.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
