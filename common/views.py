from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import TagSerializer, ReviewSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .crawlers import crawl_art_map, crawl_art_map_exhibitions, crawl_art_map_exhibitions_simple, crawl_first_exhibition, crawl_exhibition_by_url, crawl_art_map_exhibitions_selenium
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime


# Create your views here.
@extend_schema(
    summary="아트맵 웹사이트 기본 정보 크롤링",
    description="아트맵 웹사이트의 서비스, 메뉴, 연락처 정보를 크롤링합니다.",
    tags=["Crawling"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def art_map_crawler(request):
    """아트맵 웹사이트 크롤링 API"""
    result = crawl_art_map()
    return Response(result)

@extend_schema(
    summary="아트맵 전시 목록 크롤링",
    description="아트맵의 현재 전시 목록을 크롤링합니다. 각 전시의 상세 정보도 함께 수집합니다.",
    tags=["Crawling"],
    parameters=[
        OpenApiParameter(
            name="limit",
            description="결과 개수 제한 (테스트 용도)",
            required=False,
            type=int
        ),
        OpenApiParameter(
            name="debug",
            description="디버그 정보 포함 (true/false)",
            required=False,
            type=bool
        )
    ],
    responses={
        200: OpenApiResponse(description="전시회 정보 목록")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def exhibition_crawler(request):
    """아트맵 전시 목록 크롤링 API"""
    # 결과 제한 옵션 (스웨거에서 테스트할 때 유용)
    limit = request.query_params.get('limit')
    debug = request.query_params.get('debug', 'false').lower() == 'true'
    
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            limit = None
    
    try:
        # 간단한 테스트 데이터 반환 (디버그 모드)
        if debug and request.query_params.get('test', 'false').lower() == 'true':
            result = {
                "debug_mode": True,
                "message": "디버그 모드로 테스트 데이터 반환",
                "total_count": 2,
                "exhibitions": [
                    {
                        "title": "테스트 전시회 1",
                        "location": "테스트 장소",
                        "date": "2023.01.01 - 2023.12.31",
                        "image_url": "https://example.com/image.jpg",
                        "detail_url": "https://example.com/detail",
                        "description": "테스트 설명",
                        "price": "무료"
                    },
                    {
                        "title": "테스트 전시회 2",
                        "location": "테스트 장소 2",
                        "date": "2023.02.01 - 2023.11.30",
                        "image_url": "https://example.com/image2.jpg",
                        "detail_url": "https://example.com/detail2",
                        "description": "테스트 설명 2",
                        "price": "10,000원"
                    }
                ]
            }
        else:
            # 실제 크롤링 시작
            print("크롤링 시작...")
            result = crawl_art_map_exhibitions()
            print("크롤링 완료!")
            
            # 결과가 비어있는지 확인
            if not result or ('exhibitions' not in result and 'error' in result):
                error_response = {
                    "error": result.get('error', "크롤링 결과가 비어있습니다."),
                    "status": "error",
                    "crawled_at": datetime.now().isoformat()
                }
                
                # 디버그 모드면 추가 정보 포함
                if debug and 'debug_info' in result:
                    error_response["debug_info"] = result['debug_info']
                
                return Response(error_response)
        
        # 결과 제한 적용
        if limit and 'exhibitions' in result:
            result['exhibitions'] = result['exhibitions'][:limit]
            result['limited_count'] = len(result['exhibitions'])
            result['original_count'] = result.get('total_count', 0)
            result['total_count'] = len(result['exhibitions'])
        
        # 디버그 모드가 아니면 디버그 정보 제거
        if not debug and 'debug_info' in result:
            del result['debug_info']
        
        return Response(result)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return Response({
            "error": str(e),
            "error_details": error_details if debug else "자세한 오류 정보를 보려면 debug=true 파라미터를 추가하세요.",
            "status": "error",
            "crawled_at": datetime.now().isoformat()
        }, status=500)

@extend_schema(
    summary="아트맵 전시 목록 간소화 크롤링",
    description="requests와 BeautifulSoup만 사용하여 아트맵의 현재 전시 목록 기본 정보를 크롤링합니다.",
    tags=["Crawling"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def exhibition_crawler_simple(request):
    """아트맵 전시 목록 간소화 크롤링 API"""
    result = crawl_art_map_exhibitions_simple()
    return Response(result)

@extend_schema(
    summary="첫 번째 전시회 상세 정보 크롤링",
    description="아트맵에서 첫 번째 전시회의 상세 정보만 크롤링합니다.",
    tags=["Crawling"],
    parameters=[
        OpenApiParameter(
            name="debug",
            description="디버그 정보 포함 (true/false)",
            required=False,
            type=bool
        )
    ],
    responses={
        200: OpenApiResponse(description="첫 번째 전시회 상세 정보")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def first_exhibition_crawler(request):
    """첫 번째 전시회 상세 정보 크롤링 API"""
    debug = request.query_params.get('debug', 'false').lower() == 'true'
    
    try:
        # 크롤링 실행
        result = crawl_first_exhibition()
        
        # 오류 확인
        if 'error' in result and 'exhibition' not in result:
            error_response = {
                "error": result.get('error', "전시회 정보를 추출할 수 없습니다."),
                "status": "error",
                "crawled_at": datetime.now().isoformat()
            }
            
            # 디버그 모드면 추가 정보 포함
            if debug and 'debug_info' in result:
                error_response["debug_info"] = result['debug_info']
            
            return Response(error_response)
        
        # 디버그 모드가 아니면 디버그 정보 제거
        if not debug and 'debug_info' in result:
            del result['debug_info']
        
        return Response(result)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return Response({
            "error": str(e),
            "error_details": error_details if debug else "자세한 오류 정보를 보려면 debug=true 파라미터를 추가하세요.",
            "status": "error",
            "crawled_at": datetime.now().isoformat()
        }, status=500)

@extend_schema(
    summary="특정 URL의 전시회 정보 크롤링",
    description="아트맵의 특정 URL에서 전시회 정보를 크롤링합니다.",
    tags=["Crawling"],
    parameters=[
        OpenApiParameter(
            name="url",
            description="크롤링할 전시회 URL",
            required=True,
            type=str
        ),
        OpenApiParameter(
            name="debug",
            description="디버그 정보 포함 (true/false)",
            required=False,
            type=bool
        )
    ],
    responses={
        200: OpenApiResponse(description="특정 전시회 정보")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def exhibition_by_url_crawler(request):
    """특정 URL의 전시회 정보 크롤링 API"""
    url = request.query_params.get('url')
    debug = request.query_params.get('debug', 'false').lower() == 'true'
    
    if not url:
        return Response({
            "error": "URL 파라미터가 필요합니다",
            "status": "error",
            "crawled_at": datetime.now().isoformat()
        }, status=400)
    
    try:
        # 크롤링 실행
        result = crawl_exhibition_by_url(url)
        
        # 오류 확인
        if 'error' in result and 'exhibition' not in result:
            error_response = {
                "error": result.get('error', "전시회 정보를 추출할 수 없습니다."),
                "status": "error",
                "crawled_at": datetime.now().isoformat()
            }
            
            # 디버그 모드면 추가 정보 포함
            if debug and 'debug_info' in result:
                error_response["debug_info"] = result['debug_info']
            
            return Response(error_response)
        
        # 디버그 모드가 아니면 디버그 정보 제거
        if not debug and 'debug_info' in result:
            del result['debug_info']
        
        return Response(result)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return Response({
            "error": str(e),
            "error_details": error_details if debug else "자세한 오류 정보를 보려면 debug=true 파라미터를 추가하세요.",
            "status": "error",
            "crawled_at": datetime.now().isoformat()
        }, status=500)

# 크롤러 뷰 추가
@extend_schema(
    summary="전시회 목록과 상세 정보 크롤링",
    description="아트맵에서 전시회 목록과 상세 정보를 크롤링합니다.",
    tags=["Crawling"],
)
@api_view(['GET'])
@permission_classes([AllowAny])
def exhibition_crawler_api(request):
    """전시회 목록 및 상세 정보 크롤링 API"""

    try:
        # 전시회 크롤링 실행
        result = crawl_art_map_exhibitions_selenium()

        # 결과 반환
        return JsonResponse(result, safe=False)

    except Exception as e:
        # 오류 발생 시 오류 메시지 반환
        return JsonResponse({
            "error": str(e),
            "crawled_at": datetime.now().isoformat()
        }, status=500)