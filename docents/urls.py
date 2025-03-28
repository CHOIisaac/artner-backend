from rest_framework.routers import DefaultRouter
from .views import DocentViewSet, DocentItemViewSet, DocentHighlightViewSet

router = DefaultRouter()
router.register(r'docents', DocentViewSet)
router.register(r'docent-items', DocentItemViewSet)
router.register(r'docent-highlights', DocentHighlightViewSet)
router.register(r'highlights', DocentHighlightViewSet)

urlpatterns = router.urls 