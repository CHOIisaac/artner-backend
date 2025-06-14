from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from django.urls import path
from .auth_views import CustomTokenObtainPairView, CustomTokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
