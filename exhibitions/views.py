from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Exhibition, ExhibitionDetail
from .serializers import ExhibitionSerializer, ExhibitionDetailSerializer, ExhibitionDetailedSerializer

# Create your views here.

class ExhibitionViewSet(viewsets.ModelViewSet):
    queryset = Exhibition.objects.all()
    serializer_class = ExhibitionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_featured', 'venue']
    search_fields = ['title', 'description', 'venue']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExhibitionDetailedSerializer
        return ExhibitionSerializer

class ExhibitionDetailViewSet(viewsets.ModelViewSet):
    queryset = ExhibitionDetail.objects.all()
    serializer_class = ExhibitionDetailSerializer
