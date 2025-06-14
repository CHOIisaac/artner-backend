"""
Django settings for config project.
Base settings to be inherited by development.py and production.py
"""

import os
from pathlib import Path
from datetime import timedelta
from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'drf_spectacular',
    'corsheaders',
]

LOCAL_APPS = [
    'users',
    'exhibitions',
    'artworks',
    'artists',
    'docents',
    'highlights',
    'likes',
    'records',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Custom user model
AUTH_USER_MODEL = 'users.User'

# drf-spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Artner API',
    'DESCRIPTION': 'Artner project API documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY': [
        {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT 토큰을 입력하세요'
            }
        }
    ],
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Authentication', 'description': '인증 관련'},
        {'name': 'Feed', 'description': '메인 피드 서비스 (전시/작가/작품 추천 및 조회)'},
        {'name': 'Docents', 'description': '도슨트 서비스 (음성/텍스트 가이드)'},
        {'name': 'Highlights', 'description': '하이라이트 관리 (도슨트 내 중요 부분 표시)'},
        {'name': 'Collections', 'description': '사용자 컬렉션 관리 (폴더/저장/분류)'},
        {'name': 'Likes', 'description': '좋아요 관리'},
        {'name': 'Records', 'description': '기록 관리 (전시회)'},
        {'name': 'Users', 'description': '사용자 프로필'},
        {'name': 'Crawling', 'description': '전시회 크롤링'},
    ],
}


# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.getenv('DJANGO_SECRET_KEY', 'django-insecure-development-key-123'),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}
