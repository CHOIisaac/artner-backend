from rest_framework.routers import DefaultRouter
from .views import ExhibitionLikeViewSet, ArtworkLikeViewSet, ArtistLikeViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'exhibition-likes', ExhibitionLikeViewSet, basename='exhibition-like')
router.register(r'artwork-likes', ArtworkLikeViewSet, basename='artwork-like')
router.register(r'artist-likes', ArtistLikeViewSet, basename='artist-like')

urlpatterns = router.urls 