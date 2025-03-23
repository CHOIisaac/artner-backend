from rest_framework.routers import DefaultRouter
from .views import TagViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'reviews', ReviewViewSet) 