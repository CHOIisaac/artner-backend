from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from django.urls import path
from .admin_views import admin_login

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/login/', admin_login, name='admin-login'),
]
