from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import art_map_crawler, exhibition_auto_crawler_api, exhibition_fast_crawler_api, artist_fast_crawler_api

router = DefaultRouter(trailing_slash=False)

# APIView는 router에 직접 등록할 수 없으므로 별도의 urlpatterns 목록에 추가
urlpatterns = [
    path('crawl/artmap', art_map_crawler, name='art_map_crawler'),
    path('crawl/exhibitions', exhibition_auto_crawler_api, name='exhibition_crawler_api'),
    path('crawl/exhibitions/fast', exhibition_fast_crawler_api, name='exhibition_crawler_api'),
    path('crawl/artists/fast', artist_fast_crawler_api, name='artist_fast_crawler_api'),
    # path('crawl/exhibitions/simple', exhibition_crawler_simple, name='exhibition_crawler_simple'),
    # path('crawl/exhibition/first', first_exhibition_crawler, name='first_exhibition_crawler'),
    # path('crawl/exhibition/url', exhibition_by_url_crawler, name='exhibition_by_url_crawler'),
] 