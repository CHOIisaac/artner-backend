from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import User, Docent, Highlight
from ..serializers import UserSerializer, DocentSerializer, HighlightSerializer
from ..permissions import IsOwnerOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def docents(self, request, pk=None):
        user = self.get_object()
        docents = Docent.objects.filter(author=user, is_public=True)
        serializer = DocentSerializer(docents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def highlights(self, request, pk=None):
        user = self.get_object()
        highlights = Highlight.objects.filter(user=user)
        serializer = HighlightSerializer(highlights, many=True)
        return Response(serializer.data) 