from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Museum
from ..serializers import MuseumSerializer


class MuseumViewSet(viewsets.ModelViewSet):
    queryset = Museum.objects.all()
    serializer_class = MuseumSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city']
    search_fields = ['name', 'city', 'address'] 