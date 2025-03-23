from rest_framework.routers import DefaultRouter
from .views import CollectionViewSet, CollectionItemViewSet

router = DefaultRouter()
router.register(r'collections', CollectionViewSet)
router.register(r'collection-items', CollectionItemViewSet) 