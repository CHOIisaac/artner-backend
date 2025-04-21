from rest_framework.routers import DefaultRouter
from .views import DocentViewSet, DocentItemViewSet, DocentHighlightViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'docents', DocentViewSet)
router.register(r'docent-items', DocentItemViewSet)
router.register(r'highlights', DocentHighlightViewSet)

urlpatterns = router.urls 