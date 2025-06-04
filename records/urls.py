from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExhibitionRecordViewSet

router = DefaultRouter()
router.register(r'records', ExhibitionRecordViewSet, basename='record')

urlpatterns = [
    path('', include(router.urls)),
] 