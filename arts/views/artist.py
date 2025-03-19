from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Artist
from ..serializers import ArtistSerializer


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['nationality']
    search_fields = ['name', 'nationality'] 