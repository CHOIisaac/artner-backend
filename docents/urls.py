from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FolderViewSet, DocentViewSet, generate_realtime_docent, get_audio_status, stream_audio, debug_memory_jobs

router = DefaultRouter(trailing_slash=False)
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'docents', DocentViewSet, basename='docent')

urlpatterns = [
    path('', include(router.urls)),
    path('realtime-docent', generate_realtime_docent, name='generate_realtime_docent'),
    path('audio-status/<str:job_id>', get_audio_status, name='get_audio_status'),
    path('stream-audio/<str:job_id>', stream_audio, name='stream_audio'),
    path('debug/memory-jobs', debug_memory_jobs, name='debug_memory_jobs'),
] 