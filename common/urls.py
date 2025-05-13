from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import exhibition_fast_crawler_api

router = DefaultRouter(trailing_slash=False)

# APIView는 router에 직접 등록할 수 없으므로 별도의 urlpatterns 목록에 추가
urlpatterns = [
    path('crawl/exhibitions', exhibition_fast_crawler_api, name='exhibition_crawler_api'),
]