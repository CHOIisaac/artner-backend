import asyncio

import aiohttp
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .crawlers import crawl_artmap_exhibitions, save_exhibitions_to_db


# Create your views here.

@extend_schema(
    summary="고속 아트맵 전시회 크롤링",
    description="비동기 방식으로 아트맵 전시회를 빠르게 크롤링합니다.",
    tags=["Crawling"],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def exhibition_fast_crawler_api(request):
    """아트맵 전시회 고속 크롤링 API"""
    
    try:
        # 크롤링 실행
        result = crawl_artmap_exhibitions()
        
        if not result["success"]:
            return Response(result, status=500)
            
        # 크롤링된 데이터를 DB에 저장
        save_result = save_exhibitions_to_db(result["exhibitions"])
        
        # 저장 결과를 응답에 추가
        result["saved_exhibitions"] = save_result["saved_count"]
        result["updated_exhibitions"] = save_result["updated_count"]
        result["skipped_exhibitions"] = save_result["skipped_count"]
        result["message"] = f"크롤링 완료. {save_result['saved_count']}개 저장, {save_result['updated_count']}개 업데이트됨. {save_result['skipped_count']}개 건너뜀."
        
        return Response(result)
        
    except Exception as e:
        return Response({
            "success": False,
            "message": "크롤링 중 오류 발생",
            "error": str(e)
        }, status=500)