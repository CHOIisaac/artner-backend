from rest_framework.routers import DefaultRouter
from .views import ExhibitionViewSet, ExhibitionDetailViewSet

router = DefaultRouter()
router.register(r'exhibitions', ExhibitionViewSet)
router.register(r'exhibition-details', ExhibitionDetailViewSet) 