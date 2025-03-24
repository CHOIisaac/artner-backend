from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Docent, DocentItem, DocentHighlight
from users.models import User
from exhibitions.models import Exhibition

class DocentHighlightTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        self.exhibition = Exhibition.objects.create(
            title='Test Exhibition',
            description='Test Description'
        )
        
        self.docent = Docent.objects.create(
            title='Test Docent',
            description='Test Description',
            creator=self.user,
            exhibition=self.exhibition,
            type='personal'
        )
        
    def test_create_highlight(self):
        data = {
            'docent': self.docent.id,
            'text': '중요한 부분입니다',
            'start_position': 10,
            'end_position': 20,
            'color': 'yellow',
            'note': '나중에 확인할 내용'
        }
        response = self.client.post(reverse('docenthighlight-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DocentHighlight.objects.count(), 1)
        self.assertEqual(DocentHighlight.objects.get().user, self.user)
        
    def test_get_highlights(self):
        # 내 하이라이트 생성
        DocentHighlight.objects.create(
            docent=self.docent,
            text='내 하이라이트',
            start_position=10,
            end_position=20,
            user=self.user
        )
        
        # 다른 사용자의 비공개 하이라이트 생성
        other_user = User.objects.create_user(
            username='otheruser', 
            email='other@example.com', 
            password='otherpassword'
        )
        DocentHighlight.objects.create(
            docent=self.docent,
            text='다른 사용자의 비공개 하이라이트',
            start_position=30,
            end_position=40,
            user=other_user,
            is_public=False
        )
        
        # 다른 사용자의 공개 하이라이트 생성
        DocentHighlight.objects.create(
            docent=self.docent,
            text='다른 사용자의 공개 하이라이트',
            start_position=50,
            end_position=60,
            user=other_user,
            is_public=True
        )
        
        response = self.client.get(reverse('docenthighlight-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 내 하이라이트 + 다른 사용자의 공개 하이라이트 = 2개
        self.assertEqual(len(response.data), 2)
