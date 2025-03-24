from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, UserPreference
from .serializers import UserSerializer, UserPreferenceSerializer, UserDetailedSerializer
from common.mixins import DetailedSerializerMixin
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

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
