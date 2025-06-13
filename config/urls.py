"""
URL configuration for config project.

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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# ViewSet 기반 앱들의 라우터
from users.urls import router as users_router
from docents.urls import router as docents_router
from common.urls import router as common_router, urlpatterns as common_urls
from feeds.urls import router as feeds_router
from artists.urls import router as artists_router
from artworks.urls import router as artworks_router
from exhibitions.urls import router as exhibitions_router
from likes.urls import router as likes_router
from highlights.urls import router as highlights_router
from records.urls import router as records_router

# 메인 라우터 생성 (모든 ViewSet 기반 앱들)
router = DefaultRouter(trailing_slash=False)
router.registry.extend(users_router.registry)
router.registry.extend(docents_router.registry)
router.registry.extend(common_router.registry)
router.registry.extend(feeds_router.registry)
router.registry.extend(artists_router.registry)
router.registry.extend(artworks_router.registry)
router.registry.extend(exhibitions_router.registry)
router.registry.extend(likes_router.registry)
router.registry.extend(highlights_router.registry)
router.registry.extend(records_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 모든 API들 (통일된 router 기반)
    path('api/', include(router.urls)),
    
    # 기타
    path('api-auth/', include('rest_framework.urls')),
    path('api/common/', include(common_urls)),
    
    # drf-spectacular 관련 URL
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# 개발 환경에서 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "아트너 관리"
admin.site.site_title = "아트너 관리"
admin.site.index_title = "Artner"