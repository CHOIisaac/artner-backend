from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Like
from ..serializers import LikeSerializer
from ..permissions import IsOwnerOrReadOnly


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'content_type', 'object_id']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 