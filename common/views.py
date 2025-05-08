from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .crawlers import crawl_art_map, crawl_art_map_exhibitions, crawl_art_map_exhibitions_simple, crawl_first_exhibition, crawl_exhibition_by_url, crawl_art_map_exhibitions_selenium
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


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

@extend_schema(
    summary="아트맵 전시회 목록과 상세 정보 크롤링",
    description="아트맵(art-map.co.kr)에서 전시회 목록과 상세 정보를 크롤링합니다. 무한 스크롤을 시뮬레이션하여 페이지 전체를 크롤링하고, 각 전시회의 상세 페이지에서 정보를 수집합니다.",
    tags=["Crawling"],
    parameters=[
        OpenApiParameter(
            name="max_scroll",
            description="최대 스크롤 횟수 (기본값: 5)",
            required=False,
            type=int
        ),
        OpenApiParameter(
            name="scroll_delay",
            description="스크롤 간 딜레이 시간(초) (기본값: 2)",
            required=False,
            type=float
        ),
        OpenApiParameter(
            name="max_items",
            description="크롤링할 최대 항목 수 (기본값: 무제한)",
            required=False,
            type=int
        ),
        OpenApiParameter(
            name="debug",
            description="디버그 정보 포함 여부 (기본값: false)",
            required=False,
            type=bool
        )
    ],
    responses={
        200: OpenApiResponse(description="크롤링 결과"),
        500: OpenApiResponse(description="크롤링 오류")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def exhibition_crawler_api(request):
    """
    아트맵(art-map.co.kr)에서 전시회 목록과 상세 정보를 크롤링하는 API
    
    무한 스크롤을 시뮬레이션하여 전시회 목록을 크롤링하고,
    각 전시회의 상세 페이지에서 정보를 수집합니다.
    """
    # 요청 파라미터 처리
    max_scroll = int(request.data.get('max_scroll', 5))
    scroll_delay = float(request.data.get('scroll_delay', 2))
    max_items = request.data.get('max_items')
    debug = request.data.get('debug', False)
    
    if max_items:
        max_items = int(max_items)
    
    # 결과 저장 변수
    result = {
        "success": False,
        "message": "",
        "exhibitions": [],
        "total_count": 0,
        "start_time": datetime.now().isoformat()
    }
    
    driver = None
    
    try:
        # 셀레니움 설정
        start_time = datetime.now()
        result["message"] = "크롤링 시작"
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 브라우저 창 숨기기
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 웹드라이버 초기화
        driver = webdriver.Chrome(options=chrome_options)
        
        # 아트맵 전시회 목록 페이지 로드
        url = "https://art-map.co.kr/exhibition/new_list.php"
        driver.get(url)
        
        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(2)  # 초기 로딩 대기
        
        # 무한 스크롤 시뮬레이션
        exhibitions_data = []
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        for scroll in range(max_scroll):
            # 페이지 하단으로 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 스크롤 후 대기
            time.sleep(scroll_delay)
            
            # 새 컨텐츠가 로드되었는지 확인
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if debug:
                result["debug_info"] = result.get("debug_info", {})
                result["debug_info"][f"scroll_{scroll+1}"] = {
                    "previous_height": last_height,
                    "new_height": new_height,
                    "time": datetime.now().isoformat()
                }
            
            # 전시회 항목 찾기 (각 스크롤 후)
            # 실제 아트맵 사이트 구조에 맞는 선택자 사용
            items = driver.find_elements(By.CSS_SELECTOR, ".list-box .ExList, .list-box > div")
            
            if len(items) == 0:
                # 다른 선택자 시도
                items = driver.find_elements(By.CSS_SELECTOR, "[class*='exhibition'], [class*='exh']")
            
            # 수집된 전시회 데이터 길이
            current_count = len(exhibitions_data)
            
            # 새로 수집할 항목 (최대 항목 수 제한 고려)
            items_to_process = items[current_count:]
            if max_items and current_count + len(items_to_process) > max_items:
                items_to_process = items_to_process[:max_items - current_count]
            
            # 새로운 전시회 항목 정보 수집
            for idx, item in enumerate(items_to_process):
                try:
                    # 링크 추출
                    link_elem = item.find_element(By.TAG_NAME, "a")
                    detail_url = link_elem.get_attribute("href")
                    
                    # 상세 페이지 URL이 아닌 경우 건너뛰기
                    if not detail_url or not ('exhibition' in detail_url):
                        continue
                    
                    # 이미 수집한 URL인지 확인
                    if any(ex["detail_url"] == detail_url for ex in exhibitions_data):
                        continue
                    
                    # 기본 정보 수집
                    try:
                        title_elem = item.find_element(By.CSS_SELECTOR, ".ExTitle, .title, h3")
                        title = title_elem.text.strip()
                    except NoSuchElementException:
                        title = "제목 정보 없음"
                    
                    try:
                        img_elem = item.find_element(By.TAG_NAME, "img")
                        img_url = img_elem.get_attribute("src")
                    except NoSuchElementException:
                        img_url = ""
                    
                    # 전시회 목록에서 추출 가능한 기본 정보 저장
                    exhibitions_data.append({
                        "title": title,
                        "detail_url": detail_url,
                        "image_url": img_url,
                        "index": current_count + idx + 1
                    })
                    
                    # 최대 항목 수 도달 확인
                    if max_items and len(exhibitions_data) >= max_items:
                        break
                        
                except Exception as e:
                    if debug:
                        result["debug_info"] = result.get("debug_info", {})
                        result["debug_info"]["item_errors"] = result["debug_info"].get("item_errors", [])
                        result["debug_info"]["item_errors"].append({
                            "scroll": scroll + 1,
                            "item_index": current_count + idx + 1,
                            "error": str(e)
                        })
            
            # 스크롤 결과 저장
            result["scroll_progress"] = {
                "current_scroll": scroll + 1,
                "max_scroll": max_scroll,
                "items_found": len(exhibitions_data)
            }
            
            # 높이가 변경되지 않았거나, 최대 항목 수에 도달한 경우 스크롤 중단
            if new_height == last_height or (max_items and len(exhibitions_data) >= max_items):
                break
                
            last_height = new_height
        
        # 각 전시회 상세 페이지 크롤링
        result["message"] = "전시회 상세 페이지 크롤링 중..."
        
        for idx, exhibition in enumerate(exhibitions_data):
            detail_url = exhibition["detail_url"]
            
            try:
                # 상세 페이지로 이동
                driver.get(detail_url)
                time.sleep(1.5)  # 페이지 로딩 대기
                
                # 상세 정보 추출
                # 실제 아트맵 사이트 구조에 맞게 선택자 수정 필요
                exhibition_detail = {}
                
                # 제목 (이미 있지만 확인)
                try:
                    title_elem = driver.find_element(By.CSS_SELECTOR, ".ExhibitionTitle, .exhibition-title, h1.title")
                    exhibition_detail["title"] = title_elem.text.strip()
                except NoSuchElementException:
                    exhibition_detail["title"] = exhibition["title"]
                
                # 기간
                try:
                    period_elem = driver.find_element(By.CSS_SELECTOR, ".Date, .period, .date-range")
                    exhibition_detail["period"] = period_elem.text.strip()
                    
                    # 날짜 파싱 시도
                    date_match = re.search(r'(\d{4})[\./\-](\d{1,2})[\./\-](\d{1,2})\s*(?:~|-)\s*(\d{4})[\./\-](\d{1,2})[\./\-](\d{1,2})', period_elem.text)
                    if date_match:
                        start_year, start_month, start_day, end_year, end_month, end_day = map(int, date_match.groups())
                        exhibition_detail["start_date"] = f"{start_year}-{start_month:02d}-{start_day:02d}"
                        exhibition_detail["end_date"] = f"{end_year}-{end_month:02d}-{end_day:02d}"
                except NoSuchElementException:
                    exhibition_detail["period"] = ""
                
                # 장소
                try:
                    venue_elem = driver.find_element(By.CSS_SELECTOR, ".Place, .venue, .location")
                    exhibition_detail["venue"] = venue_elem.text.strip()
                except NoSuchElementException:
                    exhibition_detail["venue"] = ""
                
                # 설명
                try:
                    desc_elems = driver.find_elements(By.CSS_SELECTOR, ".Description, .description, .content")
                    exhibition_detail["description"] = "\n".join([elem.text.strip() for elem in desc_elems])
                except NoSuchElementException:
                    exhibition_detail["description"] = ""
                
                # 이미지 목록
                try:
                    img_elems = driver.find_elements(By.CSS_SELECTOR, ".ExhibitionImages img, .gallery img, .slider img")
                    exhibition_detail["images"] = [img.get_attribute("src") for img in img_elems]
                except NoSuchElementException:
                    exhibition_detail["images"] = []
                
                # 메인 이미지가 없으면 목록에서 가져온 이미지 사용
                if not exhibition_detail.get("images") and exhibition.get("image_url"):
                    exhibition_detail["images"] = [exhibition["image_url"]]
                
                # 상세 정보 병합
                exhibition.update(exhibition_detail)
                
                # 진행 상황 업데이트
                result["detail_progress"] = {
                    "current": idx + 1,
                    "total": len(exhibitions_data)
                }
                
            except Exception as e:
                if debug:
                    result["debug_info"] = result.get("debug_info", {})
                    result["debug_info"]["detail_errors"] = result["debug_info"].get("detail_errors", [])
                    result["debug_info"]["detail_errors"].append({
                        "url": detail_url,
                        "error": str(e)
                    })
                # 기본 정보만 유지
                exhibition["error"] = str(e)
        
        # 크롤링 완료
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result.update({
            "success": True,
            "message": "크롤링 완료",
            "exhibitions": exhibitions_data,
            "total_count": len(exhibitions_data),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration
        })
        
        if debug:
            result["debug_info"] = result.get("debug_info", {})
            result["debug_info"]["final_state"] = {
                "final_height": last_height,
                "total_scrolls": min(max_scroll, scroll + 1),
                "driver_closed": False
            }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        result.update({
            "success": False,
            "message": "크롤링 중 오류 발생",
            "error": str(e),
            "error_details": error_details if debug else "자세한 오류 정보를 보려면 debug=true 파라미터를 추가하세요.",
            "end_time": datetime.now().isoformat()
        })
        
    finally:
        # 웹드라이버 종료
        if driver:
            driver.quit()
            if debug and "debug_info" in result and "final_state" in result["debug_info"]:
                result["debug_info"]["final_state"]["driver_closed"] = True
    
    return Response(result)


@extend_schema(
    summary="아트맵 전시회 전체 크롤링",
    description="아트맵 전시회 목록 페이지에서 모든 전시회를 찾아 각 상세 페이지의 정보를 크롤링합니다.",
    tags=["Crawling"],
    parameters=[
        OpenApiParameter(
            name="max_scroll",
            description="최대 스크롤 횟수 (기본값: 30, 0이면 제한 없음)",
            required=False,
            type=int
        ),
        OpenApiParameter(
            name="scroll_delay",
            description="스크롤 간 딜레이(초) (기본값: 2)",
            required=False,
            type=float
        ),
        OpenApiParameter(
            name="debug",
            description="디버그 정보 포함 여부 (기본값: false)",
            required=False,
            type=bool
        )
    ],
    responses={
        200: OpenApiResponse(description="크롤링 결과"),
        500: OpenApiResponse(description="크롤링 오류")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def exhibition_auto_crawler_api(request):
    """
    아트맵 전시회 목록에서 모든 전시회를 자동으로 찾아 크롤링하는 API
    """
    # 요청 파라미터 처리
    max_scroll = int(request.data.get('max_scroll', 30))  # 기본 30회 스크롤, 0이면 제한 없음
    scroll_delay = float(request.data.get('scroll_delay', 2))
    debug = request.data.get('debug', False)

    # 결과 저장 변수
    result = {
        "success": False,
        "message": "",
        "exhibitions": [],
        "total_count": 0,
        "start_time": datetime.now().isoformat()
    }

    driver = None

    try:
        # 셀레니움 설정
        start_time = datetime.now()
        result["message"] = "크롤링 시작"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # 웹드라이버 초기화
        driver = webdriver.Chrome(options=chrome_options)

        # 메인 전시회 목록 페이지 로드
        driver.get("https://art-map.co.kr/exhibition/new_list.php")

        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(2)  # 초기 로딩 대기

        # 무한 스크롤로 모든 전시회 로드
        exhibition_links = []
        processed_links = set()  # 중복 방지를 위한 처리된 링크 집합
        scroll_count = 0
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # 스크롤 제한 확인
            if max_scroll > 0 and scroll_count >= max_scroll:
                result["message"] = f"최대 스크롤 횟수({max_scroll}회) 도달"
                break

            # 페이지 하단으로 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            scroll_count += 1

            # 스크롤 후 대기
            time.sleep(scroll_delay)

            # 현재 페이지에서 전시회 링크 찾기
            link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='view.php?idx=']")

            # 새로 발견된 링크 수 기록
            new_links_found = 0

            for link in link_elements:
                href = link.get_attribute("href")
                if href and "view.php?idx=" in href and href not in processed_links:
                    processed_links.add(href)
                    new_links_found += 1

                    try:
                        # 제목 추출
                        title_elem = link.find_element(By.CSS_SELECTOR, "#ttl_1, span[id^='ttl_']")
                        title = title_elem.text.strip()

                        # 모든 span 태그 찾기
                        spans = link.find_elements(By.CSS_SELECTOR, ".new_exh_list span")
                        venue = spans[1].text.strip() if len(spans) > 1 else ""
                        period = spans[2].text.strip() if len(spans) > 2 else ""

                        # 이미지 URL
                        img_elem = link.find_element(By.CSS_SELECTOR, "img")
                        img_url = img_elem.get_attribute("src")

                        # 기본 정보 저장
                        exhibition_links.append(href)
                        result["exhibitions"].append({
                            "detail_url": href,
                            "title": title,
                            "venue": venue,
                            "period": period,
                            "image_url": img_url,
                            "basic_info_extracted": True
                        })
                    except Exception as e:
                        # 오류 시에도 링크는 저장
                        exhibition_links.append(href)
                        result["exhibitions"].append({
                            "detail_url": href,
                            "basic_info_extracted": False,
                            "basic_extraction_error": str(e)
                        })

            # 스크롤 진행 상황 업데이트
            result["scroll_progress"] = {
                "current_scroll": scroll_count,
                "total_links_found": len(exhibition_links),
                "new_links_in_scroll": new_links_found
            }

            # 새 컨텐츠 로드 확인
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or new_links_found == 0:
                consecutive_no_new_links = result.get("consecutive_no_new_links", 0) + 1
                result["consecutive_no_new_links"] = consecutive_no_new_links

                # 3번 연속으로 새 링크가 발견되지 않으면 중단
                if consecutive_no_new_links >= 3:
                    result["message"] = "더 이상 새로운 전시회가 로드되지 않음"
                    break
            else:
                result["consecutive_no_new_links"] = 0

            last_height = new_height

        # 최종 발견된 전시회 수
        result["found_links"] = len(exhibition_links)
        result["message"] = f"{len(exhibition_links)}개의 전시회 링크 발견, 상세 정보 크롤링 중..."

        # 각 전시회 상세 페이지 크롤링
        for idx, link in enumerate(exhibition_links):
            try:
                # 상세 페이지 로드
                driver.get(link)

                # 상세 정보 추출
                exhibition_detail = {}

                # 제목 - 테이블 위의 큰 제목 찾기
                try:
                    title_elem = driver.find_element(By.CSS_SELECTOR,
                                                     "div[style*='width:1280px'][style*='text-align:center'][style*='font-size:26px']")
                    exhibition_detail["title"] = title_elem.text.strip()
                except NoSuchElementException:
                    # 기본 정보에서 제목 가져오기
                    exhibition_detail["title"] = result["exhibitions"][idx].get("title", "제목 정보 없음")

                # 테이블에서 정보 추출
                try:
                    info_table = driver.find_element(By.CSS_SELECTOR, "table")

                    # 테이블의 모든 행 추출
                    rows = info_table.find_elements(By.CSS_SELECTOR, "tr")
                    for row in rows:
                        try:
                            cells = row.find_elements(By.CSS_SELECTOR, "th, td")
                            if len(cells) >= 2:
                                header = cells[0].text.strip()
                                value = cells[1].text.strip()

                                if "기간" in header:
                                    exhibition_detail["period"] = value
                                    # 날짜 파싱
                                    date_match = re.search(
                                        r'(\d{4})[\./\-](\d{1,2})[\./\-](\d{1,2})\s*(?:~|-)\s*(\d{4})[\./\-](\d{1,2})[\./\-](\d{1,2})',
                                        value)
                                    if date_match:
                                        start_year, start_month, start_day, end_year, end_month, end_day = map(int,
                                                                                                               date_match.groups())
                                        exhibition_detail[
                                            "start_date"] = f"{start_year}-{start_month:02d}-{start_day:02d}"
                                        exhibition_detail["end_date"] = f"{end_year}-{end_month:02d}-{end_day:02d}"
                                elif "장소" in header:
                                    exhibition_detail["venue"] = value
                                elif "시간" in header:
                                    exhibition_detail["opening_hours"] = value
                                elif "휴관" in header:
                                    exhibition_detail["closed_days"] = value
                                elif "관람료" in header:
                                    exhibition_detail["price"] = value
                                elif "전화번호" in header:
                                    exhibition_detail["telephone"] = value
                                elif "작가" in header:
                                    exhibition_detail["artists"] = value
                                elif "사이트" in header:
                                    try:
                                        website_link = cells[1].find_element(By.TAG_NAME, "a")
                                        exhibition_detail["website"] = website_link.get_attribute("href")
                                    except:
                                        exhibition_detail["website"] = value
                        except Exception as e:
                            if debug:
                                result["debug_info"] = result.get("debug_info", {})
                                result["debug_info"]["row_errors"] = result["debug_info"].get("row_errors", [])
                                result["debug_info"]["row_errors"].append({
                                    "url": link,
                                    "error": str(e)
                                })
                except NoSuchElementException:
                    # 테이블을 찾지 못한 경우
                    exhibition_detail["table_found"] = False

                # 설명
                try:
                    desc_elem = driver.find_element(By.CSS_SELECTOR, ".exhibition_info")
                    exhibition_detail["description"] = desc_elem.text.strip()
                except NoSuchElementException:
                    exhibition_detail["description"] = ""

                # 이미지 목록
                try:
                    # 메인 이미지
                    main_img = driver.find_element(By.CSS_SELECTOR,
                                                   "img[style*='max-width:100%'][style*='max-height:600px']")
                    main_img_url = main_img.get_attribute("src")

                    # 추가 이미지
                    detail_images = driver.find_elements(By.CSS_SELECTOR, ".detail_image img")
                    image_urls = [main_img_url]

                    for img in detail_images:
                        img_url = img.get_attribute("src")
                        if img_url and img_url not in image_urls:
                            image_urls.append(img_url)

                    exhibition_detail["images"] = image_urls
                except NoSuchElementException:
                    # 기본 정보에서 이미지 URL 가져오기
                    exhibition_detail["images"] = [result["exhibitions"][idx].get("image_url", "")]

                # 상세 정보 업데이트
                result["exhibitions"][idx].update(exhibition_detail)

                # 진행 상황 업데이트
                result["detail_progress"] = {
                    "current": idx + 1,
                    "total": len(exhibition_links)
                }

            except Exception as e:
                if debug:
                    result["debug_info"] = result.get("debug_info", {})
                    result["debug_info"]["detail_errors"] = result["debug_info"].get("detail_errors", [])
                    result["debug_info"]["detail_errors"].append({
                        "url": link,
                        "index": idx,
                        "error": str(e)
                    })
                # 오류 정보 저장
                result["exhibitions"][idx]["error"] = str(e)

        # 크롤링 완료
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result.update({
            "success": True,
            "message": "크롤링 완료",
            "total_count": len(result["exhibitions"]),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        result.update({
            "success": False,
            "message": "크롤링 중 오류 발생",
            "error": str(e),
            "error_details": error_details if debug else "자세한 오류 정보를 보려면 debug=true 파라미터를 추가하세요.",
            "end_time": datetime.now().isoformat()
        })

    finally:
        # 웹드라이버 종료
        if driver:
            driver.quit()

    return Response(result)