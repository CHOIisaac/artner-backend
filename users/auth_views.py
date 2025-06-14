from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT 토큰을 발급받는 뷰
    username과 password를 입력받아 access token과 refresh token을 발급합니다.
    """
    pass


@extend_schema(tags=['Auth'])
class CustomTokenRefreshView(TokenRefreshView):
    """
    JWT 토큰을 갱신하는 뷰
    refresh token을 이용해 새로운 access token을 발급받습니다.
    """
    pass 