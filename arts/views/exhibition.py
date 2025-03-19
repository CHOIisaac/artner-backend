from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from ..models import Exhibition, Docent, Like
from ..serializers import ExhibitionSerializer, ExhibitionDetailSerializer, DocentSerializer


class ExhibitionViewSet(viewsets.ModelViewSet):
    queryset = Exhibition.objects.all()
    serializer_class = ExhibitionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['museum', 'is_public', 'categories']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'view_count', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExhibitionDetailSerializer
        return ExhibitionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 현재 진행 중인 전시 필터링
        ongoing = self.request.query_params.get('ongoing')
        if ongoing == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(start_date__lte=today, end_date__gte=today)
        
        # 인기 전시 필터링
        popular = self.request.query_params.get('popular')
        if popular == 'true':
            queryset = queryset.order_by('-view_count')
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def docents(self, request, pk=None):
        exhibition = self.get_object()
        docents = Docent.objects.filter(exhibition=exhibition, is_public=True)
        serializer = DocentSerializer(docents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        exhibition = self.get_object()
        user = request.user
        
        like, created = Like.objects.get_or_create(
            user=user,
            content_type='exhibition',
            object_id=exhibition.id
        )
        
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED) 