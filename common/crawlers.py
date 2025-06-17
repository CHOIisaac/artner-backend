import asyncio
import os
import re
import tempfile
import time
from datetime import date, datetime
from urllib.parse import urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup
from django.core.files import File
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from exhibitions.models import Exhibition


async def fetch_exhibition_detail(session, exhibition, semaphore):
    """전시회 상세 페이지에서 정보를 추출하는 비동기 함수"""
    # 세마포어로 동시 요청 제한
    async with semaphore:
        try:
            # 기본 정보 초기화
            detail = {
                "title": exhibition.get("title", ""),
                "venue": exhibition.get("venue", ""),
                "period": exhibition.get("period", ""),
                "image_url": exhibition.get("image_url", ""),
                "detail_url": exhibition["url"]
            }

            # 상세 페이지 요청
            async with session.get(exhibition["url"], timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # 제목 (테이블 위 큰 제목)
                    title_elem = soup.select_one(
                        "div[style*='width:1280px'][style*='text-align:center'][style*='font-size:26px']")
                    if title_elem:
                        detail["title"] = title_elem.text.strip()

                    # 테이블에서 정보 추출
                    info_table = soup.select_one("table")
                    if info_table:
                        rows = info_table.select("tr")
                        for row in rows:
                            cells = row.select("th, td")
                            if len(cells) >= 2:
                                header = cells[0].text.strip()
                                value = cells[1].text.strip()

                                if "기간" in header:
                                    detail["period"] = value
                                elif "주소" in header:
                                    detail["address"] = value
                                elif "시간" in header:
                                    detail["opening_hours"] = value
                                elif "휴관" in header:
                                    detail["closed_days"] = value
                                elif "관람료" in header:
                                    detail["price"] = value
                                elif "전화번호" in header:
                                    detail["telephone"] = value
                                elif "사이트" in header:
                                    link = cells[1].select_one("a")
                                    if link and link.get("href"):
                                        detail["website"] = link.get("href")
                                    else:
                                        detail["website"] = value
                                elif "작가" in header:
                                    detail["artists"] = value

                    # 설명
                    desc_elem = soup.select_one(".exhibition_info")
                    if desc_elem:
                        detail["description"] = desc_elem.text.strip()

                    # 이미지
                    detail["images"] = []

                    # 메인 이미지
                    main_img = soup.select_one("img[style*='max-width:100%'][style*='max-height:600px']")
                    if main_img and main_img.get("src"):
                        detail["images"].append(main_img.get("src"))

                    # 추가 이미지
                    for img in soup.select(".detail_image img"):
                        img_src = img.get("src")
                        if img_src and img_src not in detail["images"]:
                            detail["images"].append(img_src)

                    # 기본 이미지 없으면 목록 이미지 사용
                    if not detail["images"] and detail.get("image_url"):
                        detail["images"].append(detail["image_url"])

                    return detail
                else:
                    detail["error"] = f"HTTP 오류: {response.status}"
                    return detail
        except Exception as e:
            # 오류 발생 시에도 기본 정보 반환
            detail = {
                "title": exhibition.get("title", ""),
                "address": exhibition.get("address", ""),
                "period": exhibition.get("period", ""),
                "image_url": exhibition.get("image_url", ""),
                "detail_url": exhibition["url"],
                "error": str(e)
            }
            return detail


async def fetch_exhibition_details(exhibition_links):
    """모든 전시회 상세 정보를 비동기적으로 수집"""
    # 전시회 상세 정보를 저장할 리스트
    exhibitions_data = []

    # 동시 요청 수 제한 (서버에 과부하 방지)
    semaphore = asyncio.Semaphore(10)  # 최대 10개 동시 요청

    async with aiohttp.ClientSession() as session:
        # 모든 전시회 상세 정보 병렬로 가져오기
        tasks = [fetch_exhibition_detail(session, exhibition, semaphore) for exhibition in exhibition_links]
        exhibitions_data = await asyncio.gather(*tasks)

        return exhibitions_data


def get_exhibition_links():
    """아트맵 웹사이트에서 전시회 링크와 기본 정보 수집"""
    exhibition_links = []
    driver = None

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)

        # 목록 페이지 로드
        driver.get("https://art-map.co.kr/exhibition/new_list.php")
        time.sleep(2)

        # 무한 스크롤 최적화 (더 빠른 스크롤)
        processed_urls = set()
        last_height = 0
        no_new_links_count = 0

        for scroll in range(50):  # 최대 50회 스크롤
            # 페이지 하단으로 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)  # 최소한의 대기 시간

            # 현재 페이지의 모든 전시회 링크 찾기
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='view.php?idx=']")

            # 새 링크 수 카운트
            new_links_count = 0

            for link in links:
                url = link.get_attribute("href")
                if url and url not in processed_urls:
                    processed_urls.add(url)
                    new_links_count += 1

                    # 기본 정보 추출
                    try:
                        title_elem = link.find_element(By.CSS_SELECTOR, "#ttl_1, span[id^='ttl_']")
                        title = title_elem.text.strip()

                        spans = link.find_elements(By.CSS_SELECTOR, ".new_exh_list span")
                        venue = spans[1].text.strip() if len(spans) > 1 else ""
                        period = spans[2].text.strip() if len(spans) > 2 else ""

                        img_elem = link.find_element(By.CSS_SELECTOR, "img")
                        img_url = img_elem.get_attribute("src")

                        exhibition_links.append({
                            "url": url,
                            "title": title,
                            "venue": venue,
                            "period": period,
                            "image_url": img_url
                        })
                    except Exception:
                        exhibition_links.append({"url": url})

            # 새 링크가 없으면 카운트 증가
            if new_links_count == 0:
                no_new_links_count += 1
                if no_new_links_count >= 3:  # 3번 연속으로 새 링크가 없으면 종료
                    break
            else:
                no_new_links_count = 0

            # 페이지 높이 변화가 없으면 종료
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    except Exception as e:
        if driver:
            driver.quit()
        raise e

    finally:
        if driver:
            driver.quit()
    return exhibition_links


def crawl_artmap_exhibitions():
    """아트맵 웹사이트에서 전시회 정보를 크롤링하는 메인 함수"""
    result = {
        "success": False,
        "message": "크롤링 시작",
        "exhibitions": [],
        "start_time": datetime.now().isoformat()
    }

    try:
        # 1단계: 전시회 링크와 기본 정보 수집
        exhibition_links = get_exhibition_links()
        
        result["found_exhibitions"] = len(exhibition_links)
        result["message"] = f"{len(exhibition_links)}개 전시회 발견, 상세 정보 수집 중..."

        # 2단계: 비동기적으로 상세 정보 수집
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        exhibitions_data = loop.run_until_complete(fetch_exhibition_details(exhibition_links))

        # 결과 정리
        result["exhibitions"] = exhibitions_data
        result["total_count"] = len(exhibitions_data)
        result["end_time"] = datetime.now().isoformat()
        result["duration_seconds"] = (datetime.fromisoformat(result["end_time"]) -
                                    datetime.fromisoformat(result["start_time"])).total_seconds()
        result["success"] = True
        result["message"] = "크롤링 완료"

        return result

    except Exception as e:
        result["error"] = str(e)
        result["end_time"] = datetime.now().isoformat()
        return result


def save_exhibitions_to_db(exhibitions_data):
    """크롤링한 전시회 정보를 데이터베이스에 저장"""
    saved_count = 0
    updated_count = 0
    skipped_count = 0
    
    for exh_data in exhibitions_data:
        # 필수 데이터 확인
        if not exh_data.get('title') or not exh_data.get('venue') or not exh_data.get('period'):
            skipped_count += 1
            continue
            
        # 기간에서 시작일과 종료일 추출
        period = exh_data.get('period', '')
        date_pattern = r'(\d{4})[\.\-](\d{1,2})[\.\-](\d{1,2})'
        dates = re.findall(date_pattern, period)
        
        if len(dates) < 2:
            skipped_count += 1
            continue  # 시작일과 종료일을 찾을 수 없는 경우 건너뛰기
            
        # 날짜 형식 변환 (YYYY.MM.DD -> date 객체)
        try:
            start_year, start_month, start_day = dates[0]
            end_year, end_month, end_day = dates[1]
            
            start_date = date(int(start_year), int(start_month), int(start_day))
            end_date = date(int(end_year), int(end_month), int(end_day))
        except Exception as e:
            print(f"날짜 파싱 오류: {e}")
            skipped_count += 1
            continue
        
        # 기존 전시회 검색 또는 새로 생성
        try:
            exhibition, created = Exhibition.objects.update_or_create(
                title=exh_data.get('title')[:100],  # 길이 제한
                defaults={
                    'venue': exh_data.get('venue', '')[:100],  # 길이 제한
                    'start_date': start_date,
                    'end_date': end_date,
                    'museum_url': exh_data.get('website', '')[:200]  # 길이 제한
                }
            )
            
            # 이미지 다운로드 및 저장 (이미지가 있는 경우에만)
            if not exhibition.image and exh_data.get('images') and len(exh_data['images']) > 0:
                try:
                    img_url = exh_data['images'][0]
                    
                    # URL 형식 확인 및 수정
                    if img_url.startswith('/'):
                        # 상대 경로인 경우 기본 도메인 추가
                        img_url = f"https://art-map.co.kr{img_url}"
                    elif not img_url.startswith(('http://', 'https://')):
                        # 스킴이 없는 경우 https:// 추가
                        img_url = f"https://{img_url}"
                    
                    response = requests.get(img_url, stream=True)
                    if response.status_code == 200:
                        # 파일 이름 추출
                        img_filename = os.path.basename(urlparse(img_url).path)
                        if not img_filename or '.' not in img_filename:
                            img_filename = f"exhibition_{exhibition.id}.jpg"
                            
                        # 임시 파일에 저장
                        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                            for chunk in response.iter_content(chunk_size=1024):
                                if chunk:
                                    temp_file.write(chunk)
                            temp_file.flush()
                            
                            # ImageField에 저장
                            exhibition.image.save(img_filename, File(open(temp_file.name, 'rb')))
                except Exception as e:
                    print(f"이미지 다운로드 오류: {e}")
            
            # 상태 자동 저장 (save 메서드 내에서 처리됨)
            exhibition.save()
            
            if created:
                saved_count += 1
            else:
                updated_count += 1
        except Exception as e:
            print(f"전시회 저장 오류: {e}")
            skipped_count += 1
    
    return {
        "saved_count": saved_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count
    }
