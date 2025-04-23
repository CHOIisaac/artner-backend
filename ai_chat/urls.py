from django.urls import path
from .views import ChatView, ArtworkInfoView

urlpatterns = [
    path('chat', ChatView.as_view(), name='chat'),
    path('artwork-info', ArtworkInfoView.as_view(), name='artwork-info'),
] 