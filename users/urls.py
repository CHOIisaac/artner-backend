from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserPreferenceViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'user-preferences', UserPreferenceViewSet) 