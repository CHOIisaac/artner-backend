from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Exhibition, ExhibitionLike
from .serializers import ExhibitionSerializer
from drf_spectacular.utils import extend_schema
from django.db import transaction

# Create your views here.

class ExhibitionViewSet(viewsets.GenericViewSet):
    queryset = Exhibition.objects.all()
    serializer_class = ExhibitionSerializer
    
    @extend_schema(
        summary="전시회 좋아요 토글",
        description="전시회에 좋아요를 추가하거나 취소합니다.",
        tags=["Exhibitions"]
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, pk=None):
        exhibition = self.get_object()
        user = request.user
        
        # 트랜잭션으로 좋아요 처리
        with transaction.atomic():
            # 이미 좋아요한 경우 취소
            try:
                like = ExhibitionLike.objects.get(user=user, exhibition=exhibition)
                like.delete()
                
                # 좋아요 수 감소
                exhibition.likes_count = max(0, exhibition.likes_count - 1)
                exhibition.save(update_fields=['likes_count'])
                
                return Response({'status': 'like removed'}, status=status.HTTP_200_OK)
            
            # 좋아요가 없는 경우 추가
            except ExhibitionLike.DoesNotExist:
                ExhibitionLike.objects.create(user=user, exhibition=exhibition)
                
                # 좋아요 수 증가
                exhibition.likes_count += 1
                exhibition.save(update_fields=['likes_count'])
                
                return Response({'status': 'like added'}, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="전시회 좋아요 상태 확인",
        description="전시회의 좋아요 상태를 확인합니다.",
        tags=["Exhibitions"]
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def like_status(self, request, pk=None):
        exhibition = self.get_object()
        user = request.user
        
        is_liked = ExhibitionLike.objects.filter(user=user, exhibition=exhibition).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)

# @extend_schema_view(
#     list=extend_schema(description="전시회 이미지 목록을 조회합니다.", tags=["Exhibitions"]),
#     retrieve=extend_schema(description="전시회 이미지 상세 정보를 조회합니다.", tags=["Exhibitions"]),
#     create=extend_schema(description="새로운 전시회 이미지를 생성합니다.", tags=["Exhibitions"]),
#     update=extend_schema(description="전시회 이미지 정보를 업데이트합니다.", tags=["Exhibitions"]),
#     partial_update=extend_schema(description="전시회 이미지 정보를 부분 업데이트합니다.", tags=["Exhibitions"]),
#     destroy=extend_schema(description="전시회 이미지를 삭제합니다.", tags=["Exhibitions"])
# )
# class ExhibitionImageViewSet(viewsets.ModelViewSet):
#     queryset = ExhibitionImage.objects.all()
#     serializer_class = ExhibitionImageSerializer
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['exhibition']
#     ordering_fields = ['order']
