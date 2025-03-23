from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Collection, CollectionItem
from .serializers import CollectionSerializer, CollectionItemSerializer, CollectionDetailedSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'is_public']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectionDetailedSerializer
        return CollectionSerializer


class CollectionItemViewSet(viewsets.ModelViewSet):
    queryset = CollectionItem.objects.all()
    serializer_class = CollectionItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['collection', 'artwork']
    ordering_fields = ['order', 'created_at']