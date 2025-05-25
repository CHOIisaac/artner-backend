from rest_framework.routers import DefaultRouter
from .views import FeedViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'feeds', FeedViewSet, basename='feeds')

urlpatterns = router.urls 