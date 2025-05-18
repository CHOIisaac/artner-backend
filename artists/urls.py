from rest_framework.routers import DefaultRouter
from .views import ArtistViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'artists', ArtistViewSet)

urlpatterns = router.urls 