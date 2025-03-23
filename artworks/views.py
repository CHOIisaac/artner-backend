from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Artwork, ArtworkDetail
from .serializers import ArtworkSerializer, ArtworkDetailSerializer, ArtworkDetailedSerializer

# Create your views here.

class ArtworkViewSet(viewsets.ModelViewSet):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'artist', 'exhibition', 'is_featured']
    search_fields = ['title', 'artist', 'description']
    ordering_fields = ['created_at', 'year', 'title']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArtworkDetailedSerializer
        return ArtworkSerializer

class ArtworkDetailViewSet(viewsets.ModelViewSet):
    queryset = ArtworkDetail.objects.all()
    serializer_class = ArtworkDetailSerializer
