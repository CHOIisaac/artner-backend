from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Docent, DocentItem
from .serializers import DocentSerializer, DocentItemSerializer, DocentDetailedSerializer

# Create your views here.

class DocentViewSet(viewsets.ModelViewSet):
    queryset = Docent.objects.all()
    serializer_class = DocentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_public', 'exhibition', 'creator']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'view_count', 'like_count', 'duration']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DocentDetailedSerializer
        return DocentSerializer

class DocentItemViewSet(viewsets.ModelViewSet):
    queryset = DocentItem.objects.all()
    serializer_class = DocentItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['docent', 'artwork']
    ordering_fields = ['order', 'duration']
