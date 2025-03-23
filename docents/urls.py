from rest_framework.routers import DefaultRouter
from .views import DocentViewSet, DocentItemViewSet

router = DefaultRouter()
router.register(r'docents', DocentViewSet)
router.register(r'docent-items', DocentItemViewSet) 