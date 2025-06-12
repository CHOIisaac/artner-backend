from rest_framework.routers import DefaultRouter
from .views import FolderViewSet, FolderItemViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'items', FolderItemViewSet, basename='folder-item')

urlpatterns = router.urls 