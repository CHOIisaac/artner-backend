from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from exhibitions.models import Exhibition, ExhibitionLike
from artworks.models import Artwork, ArtworkLike
from artists.models import Artist, ArtistLike
from .serializers import ExhibitionLikeSerializer, ArtworkLikeSerializer, ArtistLikeSerializer


@extend_schema_view(
    list=extend_schema(description="전시회 좋아요 목록을 조회합니다.", tags=["Likes"]),
    retrieve=extend_schema(description="전시회 좋아요 상세 정보를 조회합니다.", tags=["Likes"])
)
class ExhibitionLikeViewSet(viewsets.ModelViewSet):
    """전시회 좋아요 관리를 위한 ViewSet"""
    serializer_class = ExhibitionLikeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'exhibition']
    http_method_names = ['get', 'post', 'delete']  # PUT, PATCH 메서드 비활성화
    
    def get_queryset(self):
        """로그인한 사용자의 좋아요 또는 공개된 좋아요만 조회 가능"""
        return ExhibitionLike.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """좋아요 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        request={"application/json": {"example": {"exhibition_id": 1}}},
        responses={
            201: {"description": "좋아요가 생성되었습니다."},
            200: {"description": "좋아요가 삭제되었습니다."}
        },
        description="전시회에 좋아요를 추가하거나 취소합니다.",
        tags=["Likes"]
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """전시회 좋아요 토글"""
        exhibition_id = request.data.get('exhibition_id')
        if not exhibition_id:
            return Response(
                {"error": "exhibition_id가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exhibition = get_object_or_404(Exhibition, id=exhibition_id)
        user = request.user
        
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
        parameters=[
            OpenApiParameter(name='exhibition_id', description='전시회 ID', required=True, type=OpenApiTypes.INT)
        ],
        responses={200: {"description": "좋아요 상태", "example": {"is_liked": True}}},
        description="전시회의 좋아요 상태를 확인합니다.",
        tags=["Likes"]
    )
    @action(detail=False, methods=['get'])
    def status(self, request):
        """전시회 좋아요 상태 확인"""
        exhibition_id = request.query_params.get('exhibition_id')
        if not exhibition_id:
            return Response(
                {"error": "exhibition_id 쿼리 파라미터가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exhibition = get_object_or_404(Exhibition, id=exhibition_id)
        user = request.user
        
        is_liked = ExhibitionLike.objects.filter(user=user, exhibition=exhibition).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(description="작품 좋아요 목록을 조회합니다.", tags=["Likes"]),
    retrieve=extend_schema(description="작품 좋아요 상세 정보를 조회합니다.", tags=["Likes"])
)
class ArtworkLikeViewSet(viewsets.ModelViewSet):
    """작품 좋아요 관리를 위한 ViewSet"""
    serializer_class = ArtworkLikeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'artwork']
    http_method_names = ['get', 'post', 'delete']  # PUT, PATCH 메서드 비활성화
    
    def get_queryset(self):
        """로그인한 사용자의 좋아요만 조회 가능"""
        return ArtworkLike.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """좋아요 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        request={"application/json": {"example": {"artwork_id": 1}}},
        responses={
            201: {"description": "좋아요가 생성되었습니다."},
            200: {"description": "좋아요가 삭제되었습니다."}
        },
        description="작품에 좋아요를 추가하거나 취소합니다.",
        tags=["Likes"]
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """작품 좋아요 토글"""
        artwork_id = request.data.get('artwork_id')
        if not artwork_id:
            return Response(
                {"error": "artwork_id가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        artwork = get_object_or_404(Artwork, id=artwork_id)
        user = request.user
        
        # 이미 좋아요한 경우 취소
        try:
            like = ArtworkLike.objects.get(user=user, artwork=artwork)
            like.delete()
            
            # 좋아요 수 감소
            artwork.likes_count = max(0, artwork.likes_count - 1)
            artwork.save(update_fields=['likes_count'])
            
            return Response({'status': 'like removed'}, status=status.HTTP_200_OK)
        
        # 좋아요가 없는 경우 추가
        except ArtworkLike.DoesNotExist:
            ArtworkLike.objects.create(user=user, artwork=artwork)
            
            # 좋아요 수 증가
            artwork.likes_count += 1
            artwork.save(update_fields=['likes_count'])
            
            return Response({'status': 'like added'}, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='artwork_id', description='작품 ID', required=True, type=OpenApiTypes.INT)
        ],
        responses={200: {"description": "좋아요 상태", "example": {"is_liked": True}}},
        description="작품의 좋아요 상태를 확인합니다.",
        tags=["Likes"]
    )
    @action(detail=False, methods=['get'])
    def status(self, request):
        """작품 좋아요 상태 확인"""
        artwork_id = request.query_params.get('artwork_id')
        if not artwork_id:
            return Response(
                {"error": "artwork_id 쿼리 파라미터가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        artwork = get_object_or_404(Artwork, id=artwork_id)
        user = request.user
        
        is_liked = ArtworkLike.objects.filter(user=user, artwork=artwork).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(description="작가 좋아요 목록을 조회합니다.", tags=["Likes"]),
    retrieve=extend_schema(description="작가 좋아요 상세 정보를 조회합니다.", tags=["Likes"])
)
class ArtistLikeViewSet(viewsets.ModelViewSet):
    """작가 좋아요 관리를 위한 ViewSet"""
    serializer_class = ArtistLikeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'artist']
    http_method_names = ['get', 'post', 'delete']  # PUT, PATCH 메서드 비활성화
    
    def get_queryset(self):
        """로그인한 사용자의 좋아요만 조회 가능"""
        return ArtistLike.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """좋아요 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        request={"application/json": {"example": {"artist_id": 1}}},
        responses={
            201: {"description": "좋아요가 생성되었습니다."},
            200: {"description": "좋아요가 삭제되었습니다."}
        },
        description="작가에 좋아요를 추가하거나 취소합니다.",
        tags=["Likes"]
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """작가 좋아요 토글"""
        artist_id = request.data.get('artist_id')
        if not artist_id:
            return Response(
                {"error": "artist_id가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        artist = get_object_or_404(Artist, id=artist_id)
        user = request.user
        
        # 이미 좋아요한 경우 취소
        try:
            like = ArtistLike.objects.get(user=user, artist=artist)
            like.delete()
            
            # 좋아요 수 감소
            artist.likes_count = max(0, artist.likes_count - 1)
            artist.save(update_fields=['likes_count'])
            
            return Response({'status': 'like removed'}, status=status.HTTP_200_OK)
        
        # 좋아요가 없는 경우 추가
        except ArtistLike.DoesNotExist:
            ArtistLike.objects.create(user=user, artist=artist)
            
            # 좋아요 수 증가
            artist.likes_count += 1
            artist.save(update_fields=['likes_count'])
            
            return Response({'status': 'like added'}, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='artist_id', description='작가 ID', required=True, type=OpenApiTypes.INT)
        ],
        responses={200: {"description": "좋아요 상태", "example": {"is_liked": True}}},
        description="작가의 좋아요 상태를 확인합니다.",
        tags=["Likes"]
    )
    @action(detail=False, methods=['get'])
    def status(self, request):
        """작가 좋아요 상태 확인"""
        artist_id = request.query_params.get('artist_id')
        if not artist_id:
            return Response(
                {"error": "artist_id 쿼리 파라미터가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        artist = get_object_or_404(Artist, id=artist_id)
        user = request.user
        
        is_liked = ArtistLike.objects.filter(user=user, artist=artist).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)
