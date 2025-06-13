from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FolderViewSet, FolderItemViewSet, DocentScriptViewSet, generate_realtime_docent

router = DefaultRouter(trailing_slash=False)
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'folder-items', FolderItemViewSet, basename='folder-item')
router.register(r'docents', DocentScriptViewSet, basename='docent')

urlpatterns = [
    path('', include(router.urls)),
    path('realtime-docent/', generate_realtime_docent, name='realtime-docent'),
] 