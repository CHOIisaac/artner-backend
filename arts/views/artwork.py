from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Artwork, Like
from ..serializers import ArtworkSerializer


class ArtworkViewSet(viewsets.ModelViewSet):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['artist', 'exhibition', 'medium']
    search_fields = ['title', 'description', 'artist__name']
    ordering_fields = ['year', 'created_at']
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        artwork = self.get_object()
        user = request.user
        
        like, created = Like.objects.get_or_create(
            user=user,
            content_type='artwork',
            object_id=artwork.id
        )
        
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED) 