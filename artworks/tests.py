from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Artwork
from users.models import User

# Create your tests here.

class ArtworkTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        self.artwork = Artwork.objects.create(
            title='Test Artwork',
            artist='Test Artist',
            description='Test Description'
        )
        
    def test_get_all_artworks(self):
        response = self.client.get(reverse('artwork-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_artwork(self):
        data = {
            'title': 'New Artwork',
            'artist': 'New Artist',
            'description': 'New Description'
        }
        response = self.client.post(reverse('artwork-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
