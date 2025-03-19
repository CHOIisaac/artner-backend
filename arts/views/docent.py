from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Docent, Like
from ..serializers import DocentSerializer
from ..permissions import IsOwnerOrReadOnly


class DocentViewSet(viewsets.ModelViewSet):
    queryset = Docent.objects.filter(is_public=True)
    serializer_class = DocentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['exhibition', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['view_count', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        docent = self.get_object()
        user = request.user
        
        like, created = Like.objects.get_or_create(
            user=user,
            content_type='docent',
            object_id=docent.id
        )
        
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED) 