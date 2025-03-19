from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Highlight
from ..serializers import HighlightSerializer
from ..permissions import IsOwnerOrReadOnly


class HighlightViewSet(viewsets.ModelViewSet):
    queryset = Highlight.objects.all()
    serializer_class = HighlightSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'artwork']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 