from rest_framework.routers import DefaultRouter
from .views import DocentHighlightViewSet, SaveFolderViewSet, SavedItemViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'folders', SaveFolderViewSet, basename='save-folder')
router.register(r'items', SavedItemViewSet, basename='saved-item')
router.register(r'highlights', DocentHighlightViewSet)

urlpatterns = router.urls 