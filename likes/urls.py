from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LikedItemsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'likes', LikedItemsViewSet, basename='likes')

