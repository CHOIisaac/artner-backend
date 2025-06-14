from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

@extend_schema(
    tags=['Admin'],
    description='어드민 로그인 API',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': '관리자 아이디'},
                'password': {'type': 'string', 'description': '비밀번호'}
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: {
            'description': '로그인 성공',
            'type': 'object',
            'properties': {
                'access': {'type': 'string', 'description': 'JWT 액세스 토큰'},
                'refresh': {'type': 'string', 'description': 'JWT 리프레시 토큰'},
                'user': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'is_staff': {'type': 'boolean'}
                    }
                }
            }
        },
        401: {'description': '인증 실패'}
    },
    examples=[
        OpenApiExample(
            'Success Response',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'username': 'admin',
                    'is_staff': True
                }
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """어드민 로그인 API
    
    관리자 계정으로 로그인하고 JWT 토큰을 발급받습니다.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': '아이디와 비밀번호를 모두 입력해주세요.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is not None and user.is_staff:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'username': user.username,
                'is_staff': user.is_staff
            }
        })
    
    return Response(
        {'error': '관리자 계정이 아니거나 인증에 실패했습니다.'}, 
        status=status.HTTP_401_UNAUTHORIZED
    ) 