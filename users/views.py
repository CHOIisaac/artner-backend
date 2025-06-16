from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    me=extend_schema(
        description="현재 로그인한 사용자 자신의 정보를 조회합니다.",
        tags=["Users"]
    )
)
class UserViewSet(viewsets.GenericViewSet):
    """사용자 본인 정보 조회만 제공하는 ViewSet"""
    queryset = User.objects.all()  # 라우터 등록에 필요
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """현재 로그인한 사용자 정보 조회"""
        user = request.user
        if user.is_authenticated:
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)