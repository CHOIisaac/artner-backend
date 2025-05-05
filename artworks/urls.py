from rest_framework.routers import DefaultRouter
from .views import ArtworkViewSet

router = DefaultRouter()
router.register(r'artworks', ArtworkViewSet)
