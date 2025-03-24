from rest_framework.routers import DefaultRouter
from .views import ExhibitionViewSet

router = DefaultRouter()
router.register(r'exhibitions', ExhibitionViewSet)
# router.register(r'exhibition-images', ExhibitionImageViewSet)