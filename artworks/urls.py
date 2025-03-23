from rest_framework.routers import DefaultRouter
from .views import ArtworkViewSet, ArtworkDetailViewSet

router = DefaultRouter()
router.register(r'artworks', ArtworkViewSet)
router.register(r'artwork-details', ArtworkDetailViewSet) 