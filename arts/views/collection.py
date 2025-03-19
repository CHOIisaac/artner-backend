from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Collection, CollectionItem
from ..serializers import CollectionSerializer, CollectionItemSerializer
from ..permissions import IsOwnerOrReadOnly


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'is_public']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            # 자신의 컬렉션은 모두 볼 수 있음
            return queryset.filter(user=self.request.user) | queryset.filter(is_public=True)
        # 비로그인 사용자는 공개 컬렉션만 볼 수 있음
        return queryset.filter(is_public=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        collection = self.get_object()
        items = CollectionItem.objects.filter(collection=collection)
        serializer = CollectionItemSerializer(items, many=True)
        return Response(serializer.data)


class CollectionItemViewSet(viewsets.ModelViewSet):
    queryset = CollectionItem.objects.all()
    serializer_class = CollectionItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            # 자신의 컬렉션 아이템만 볼 수 있음
            return queryset.filter(collection__user=self.request.user)
        return queryset.none()
    
    def perform_create(self, serializer):
        collection_id = self.request.data.get('collection')
        collection = Collection.objects.get(id=collection_id)
        
        # 자신의 컬렉션에만 아이템 추가 가능
        if collection.user != self.request.user:
            return Response(
                {'detail': '자신의 컬렉션에만 아이템을 추가할 수 있습니다.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save(collection=collection) 