"""
URL configuration for artner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
# drf-yasg 관련 import 제거
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
from rest_framework import permissions
# drf-spectacular 관련 import 추가
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# 각 앱의 라우터 가져오기
from users.urls import router as users_router
from exhibitions.urls import router as exhibitions_router
from artworks.urls import router as artworks_router
from docents.urls import router as docents_router
from art_collections.urls import router as collections_router  # 수정: collections -> art_collections
from common.urls import router as common_router

# 메인 라우터 생성
router = DefaultRouter()
router.registry.extend(users_router.registry)
router.registry.extend(exhibitions_router.registry)
router.registry.extend(artworks_router.registry)
router.registry.extend(docents_router.registry)
router.registry.extend(collections_router.registry)
router.registry.extend(common_router.registry)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    
    # drf-spectacular 관련 URL 추가
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# 개발 환경에서 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
