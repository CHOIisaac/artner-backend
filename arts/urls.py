from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ArtistViewSet, MuseumViewSet, ExhibitionViewSet, 
    ArtworkViewSet, DocentViewSet, HighlightViewSet, LikeViewSet,
    CollectionViewSet, CollectionItemViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'artists', ArtistViewSet)
router.register(r'museums', MuseumViewSet)
router.register(r'exhibitions', ExhibitionViewSet)
router.register(r'artworks', ArtworkViewSet)
router.register(r'docents', DocentViewSet)
router.register(r'highlights', HighlightViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'collection-items', CollectionItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
] 