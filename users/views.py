from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, UserPreference
from .serializers import UserSerializer, UserPreferenceSerializer, UserDetailedSerializer
from common.mixins import DetailedSerializerMixin
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from exhibitions.models import Exhibition, ExhibitionLike
from exhibitions.serializers import ExhibitionSerializer
from artworks.models import Artwork, ArtworkLike
from artworks.serializers import ArtworkSerializer
from artists.models import Artist, ArtistLike
from artists.serializers import ArtistSerializer

# Create your views here.

@extend_schema_view(
    list=extend_schema(
        description="사용자 목록을 조회합니다.",
        tags=["Users"]
    ),
    retrieve=extend_schema(
        description="사용자 상세 정보를 조회합니다.",
        tags=["Users"]
    ),
    create=extend_schema(
        description="새로운 사용자를 생성합니다.",
        tags=["Users"]
    ),
    update=extend_schema(
        description="사용자 정보를 업데이트합니다.",
        tags=["Users"]
    ),
    partial_update=extend_schema(
        description="사용자 정보를 부분 업데이트합니다.",
        tags=["Users"]
    ),
    destroy=extend_schema(
        description="사용자를 삭제합니다.",
        tags=["Users"]
    )
)
class UserViewSet(DetailedSerializerMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    detailed_serializer_class = UserDetailedSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'is_staff']
    search_fields = ['username', 'email', 'nickname']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailedSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        user = request.user
        if user.is_authenticated:
            serializer = UserDetailedSerializer(user)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='검색어', required=False, type=OpenApiTypes.STR)
        ],
        description="사용자가 좋아요한 전시회 목록을 조회합니다.",
        tags=["Users"]
    )
    @action(detail=True, methods=['get'])
    def liked_exhibitions(self, request, pk=None):
        user = self.get_object()
        search_query = request.query_params.get('search', '')
        
        # 사용자가 좋아요한 전시회 ID 목록 가져오기
        liked_exhibition_ids = ExhibitionLike.objects.filter(
            user=user
        ).values_list('exhibition_id', flat=True)
        
        # 해당 전시회들 조회 및 검색 필터링
        exhibitions = Exhibition.objects.filter(
            id__in=liked_exhibition_ids
        )
        
        if search_query:
            exhibitions = exhibitions.filter(
                title__icontains=search_query
            )
            
        serializer = ExhibitionSerializer(exhibitions, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='검색어', required=False, type=OpenApiTypes.STR)
        ],
        description="사용자가 좋아요한 작품 목록을 조회합니다.",
        tags=["Users"]
    )
    @action(detail=True, methods=['get'])
    def liked_artworks(self, request, pk=None):
        user = self.get_object()
        search_query = request.query_params.get('search', '')
        
        # 사용자가 좋아요한 작품 ID 목록 가져오기
        liked_artwork_ids = ArtworkLike.objects.filter(
            user=user
        ).values_list('artwork_id', flat=True)
        
        # 해당 작품들 조회 및 검색 필터링
        artworks = Artwork.objects.filter(
            id__in=liked_artwork_ids
        )
        
        if search_query:
            artworks = artworks.filter(
                title__icontains=search_query
            )
            
        serializer = ArtworkSerializer(artworks, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='검색어', required=False, type=OpenApiTypes.STR)
        ],
        description="사용자가 좋아요한 작가 목록을 조회합니다.",
        tags=["Users"]
    )
    @action(detail=True, methods=['get'])
    def liked_artists(self, request, pk=None):
        user = self.get_object()
        search_query = request.query_params.get('search', '')
        
        # 사용자가 좋아요한 작가 ID 목록 가져오기
        liked_artist_ids = ArtistLike.objects.filter(
            user=user
        ).values_list('artist_id', flat=True)
        
        # 해당 작가들 조회 및 검색 필터링
        artists = Artist.objects.filter(
            id__in=liked_artist_ids
        )
        
        if search_query:
            artists = artists.filter(
                name__icontains=search_query
            )
            
        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)

@extend_schema_view(
    list=extend_schema(
        description="사용자 취향 목록을 조회합니다.",
        tags=["Users"]
    ),
    retrieve=extend_schema(
        description="사용자 취향 상세 정보를 조회합니다.",
        tags=["Users"]
    ),
    create=extend_schema(
        description="새로운 사용자 취향을 생성합니다.",
        tags=["Users"]
    ),
    update=extend_schema(
        description="사용자 취향 정보를 업데이트합니다.",
        tags=["Users"]
    ),
    partial_update=extend_schema(
        description="사용자 취향 정보를 부분 업데이트합니다.",
        tags=["Users"]
    ),
    destroy=extend_schema(
        description="사용자 취향을 삭제합니다.",
        tags=["Users"]
    )
)
class UserPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']
