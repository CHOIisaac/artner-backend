from rest_framework.routers import DefaultRouter
from .views import SaveFolderViewSet, SaveItemViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'folders', SaveFolderViewSet, basename='save-folder')
router.register(r'items', SaveItemViewSet, basename='save-item')

urlpatterns = router.urls 