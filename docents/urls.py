from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FolderViewSet, FolderItemViewSet, generate_realtime_docent, get_audio_status, stream_audio

router = DefaultRouter(trailing_slash=False)
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'folder-items', FolderItemViewSet, basename='folder-item')

urlpatterns = [
    path('', include(router.urls)),
    path('realtime-docent', generate_realtime_docent, name='realtime-docent'),
    path('audio/<str:job_id>', get_audio_status, name='audio-status'),
    path('audio/<str:job_id>/stream', stream_audio, name='audio-stream'),
] 