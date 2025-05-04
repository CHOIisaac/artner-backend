# 크롤링 코드 이동 
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def crawl_art_map():
    """아트맵 웹사이트 크롤링"""
    url = "https://art-map.co.kr/about/about_all.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # 웹사이트 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 오류 발생 시 예외 발생
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 서비스 정보 추출
        services = []
        
        # 서비스 카드 찾기 (주요 상품/서비스)
        service_sections = soup.select('.product-box, .service-item')
        
        if not service_sections:
            # 대체 선택자 시도
            service_sections = soup.select('div[class*="product"], div[class*="service"]')
        
        for section in service_sections:
            # 제목과 설명 추출
            title_elem = section.select_one('h3, .title, strong')
            desc_elem = section.select_one('p, .description')
            
            # 텍스트 추출 및 정리
            title = title_elem.text.strip() if title_elem else "제목 없음"
            description = desc_elem.text.strip() if desc_elem else "설명 없음"
            
            services.append({
                "title": title,
                "description": description,
                "source": "아트맵"
            })
        
        # 메뉴 항목 추출
        menu_items = soup.select('nav a, .menu a, header a')
        menu_list = []
        
        for item in menu_items:
            menu_text = item.text.strip()
            menu_link = item.get('href', '')
            
            if menu_text and not menu_text.isspace():
                menu_list.append({
                    "menu_name": menu_text,
                    "link": menu_link
                })
        
        # 연락처 정보 추출
        contact_info = {}
        footer = soup.select_one('footer, .footer')
        
        if footer:
            emails = footer.select('a[href^="mailto:"]')
            for email in emails:
                email_text = email.text.strip()
                if email_text:
                    contact_info["email"] = email_text
            
            # 회사명, 사업자등록번호 등 추출
            company_info = footer.select('p, div')
            for info in company_info:
                info_text = info.text.strip()
                if '상호명' in info_text:
                    contact_info["company_name"] = info_text
                elif '사업자등록번호' in info_text:
                    contact_info["business_number"] = info_text
        
        return {
            "services": services,
            "menus": menu_list,
            "contact": contact_info,
            "crawled_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"아트맵 크롤링 중 오류 발생: {e}")
        return {
            "error": str(e),
            "crawled_at": datetime.now().isoformat()
        }

def crawl_art_map_exhibitions():
    """아트맵 현재 전시 목록을 상세 정보와 함께 크롤링"""
    url = "https://art-map.co.kr/exhibition/new_list.php?cate=&od=2&area=&type=ing"
    debug_info = {
        "steps": [],
        "errors": []
    }
    
    try:
        debug_info["steps"].append("목록 페이지 요청 시작")
        # 헤더 설정
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # 목록 페이지 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        debug_info["steps"].append("HTML 파싱 완료")
        
        # HTML 구조 분석 (디버깅용)
        html_sample = soup.prettify()[:1000]
        debug_info["html_sample"] = html_sample
        
        # 여러 선택자 시도
        exhibition_items = soup.select(".new_exh_list")
        if not exhibition_items:
            debug_info["steps"].append("기본 선택자로 항목 찾지 못함, 대체 선택자 시도")
            # 대체 선택자 시도
            exhibition_items = soup.select("[class*='exh']")
        
        if not exhibition_items:
            debug_info["steps"].append("클래스 기반 선택자 실패, 링크 기반 시도")
            # 전시회 링크로 찾기 시도
            exhibition_items = soup.select("a[href*='exhibition/view.php']")
        
        if not exhibition_items:
            # 일반적인 리스트 항목 찾기
            debug_info["steps"].append("링크 기반 선택자 실패, 일반 리스트 항목 시도")
            exhibition_items = soup.select("ul li")
        
        if not exhibition_items:
            debug_info["errors"].append("모든 선택자로 전시회 목록을 찾을 수 없음")
            # 전체 HTML 구조 분석 (로깅)
            all_div_classes = [div.get('class', []) for div in soup.select('div[class]')]
            all_links = [a.get('href') for a in soup.select('a[href]')]
            debug_info["div_classes"] = all_div_classes[:20]  # 너무 길지 않게 20개만
            debug_info["links"] = all_links[:20]  # 너무 길지 않게 20개만
            
            return {
                "error": "전시회 목록을 찾을 수 없습니다",
                "debug_info": debug_info,
                "crawled_at": datetime.now().isoformat()
            }
        
        # 전시회 목록 정보 수집
        debug_info["steps"].append(f"전시회 항목 {len(exhibition_items)}개 발견")
        exhibitions = []
        
        # 각 전시회 항목 처리
        for idx, item in enumerate(exhibition_items):
            try:
                # 상세 페이지 URL 추출
                # 항목이 a 태그인 경우
                if item.name == 'a':
                    detail_url = item.get("href", "")
                # 다른 경우 내부에서 a 태그 찾기
                else:
                    link_elem = item.select_one("a")
                    if not link_elem:
                        debug_info["errors"].append(f"항목 {idx+1}: 링크를 찾을 수 없음")
                        continue
                    detail_url = link_elem.get("href", "")
                
                if not detail_url:
                    debug_info["errors"].append(f"항목 {idx+1}: 링크 URL이 비어있음")
                    continue
                
                # 전시회 URL인지 확인
                if not ('exhibition/view.php' in detail_url or 'exhibition/detail' in detail_url):
                    debug_info["errors"].append(f"항목 {idx+1}: 전시회 URL이 아님 - {detail_url}")
                    continue
                
                # 상세 페이지 URL이 상대 경로인 경우 절대 경로로 변환
                if not detail_url.startswith(('http://', 'https://')):
                    detail_url = f"https://art-map.co.kr{detail_url}"
                
                debug_info["steps"].append(f"항목 {idx+1}: 상세 페이지 크롤링 시작 - {detail_url}")
                
                # 상세 페이지 크롤링
                exhibition_detail = crawl_exhibition_by_url(detail_url)
                
                # 상세 정보 추출 성공 여부 확인
                if "exhibition" in exhibition_detail:
                    exhibitions.append(exhibition_detail["exhibition"])
                    debug_info["steps"].append(f"항목 {idx+1}: 상세 정보 추출 성공")
                else:
                    debug_info["errors"].append(f"항목 {idx+1}: 상세 정보 추출 실패 - {exhibition_detail.get('error', '알 수 없는 오류')}")
                
                # 서버 부하 방지 딜레이
                time.sleep(1.5)
                
                # 처음 5개만 크롤링 (테스트 용도)
                if idx >= 4:  # 0부터 시작하므로 4는 5번째 항목
                    debug_info["steps"].append("테스트를 위해 처음 5개 항목만 크롤링")
                    break
                
            except Exception as e:
                debug_info["errors"].append(f"항목 {idx+1} 처리 중 오류: {str(e)}")
                continue
        
        # 결과 반환
        return {
            "exhibitions": exhibitions,
            "total_count": len(exhibitions),
            "source_url": url,
            "crawled_at": datetime.now().isoformat(),
            "debug_info": debug_info
        }
        
    except Exception as e:
        import traceback
        debug_info["critical_error"] = str(e)
        debug_info["traceback"] = traceback.format_exc()
        
        return {
            "error": str(e),
            "debug_info": debug_info,
            "crawled_at": datetime.now().isoformat()
        }

def crawl_art_map_exhibitions_simple():
    """아트맵 현재 전시 목록 - 간소화된 크롤링 (기본 정보만)"""
    url = "https://art-map.co.kr/exhibition/new_list.php?cate=&od=2&area=&type=ing"
    
    try:
        # 간단한 헤더 설정
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # requests 라이브러리로 시도
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # 가장 기본적인 정보만 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 전시 목록 찾기 시도
        exhibitions = []
        items = soup.select(".new_exh_list")
        
        for item in items:
            try:
                # 제목
                title_elem = item.select_one("span.title")
                title = title_elem.text.strip() if title_elem else ""
                
                # 이미지
                img_elem = item.select_one("img")
                image_url = img_elem.get("src") if img_elem else ""
                
                # 링크
                link_elem = item.select_one("a")
                detail_url = link_elem.get("href") if link_elem else ""
                
                # 유효한 데이터만 추가
                if title:
                    exhibitions.append({
                        "title": title,
                        "image_url": image_url,
                        "detail_url": detail_url
                    })
            except Exception as e:
                print(f"항목 파싱 오류: {e}")
                continue
        
        if not exhibitions:
            return {
                "error": "전시회 정보를 찾을 수 없습니다",
                "html_sample": soup.prettify()[:1000],
                "crawled_at": datetime.now().isoformat()
            }
        
        return {
            "exhibitions": exhibitions,
            "total_count": len(exhibitions),
            "source_url": url,
            "crawled_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "crawled_at": datetime.now().isoformat()
        }

def crawl_first_exhibition():
    """아트맵에서 첫 번째 전시회의 상세 정보만 크롤링"""
    url = "https://art-map.co.kr/exhibition/new_list.php?cate=&od=2&area=&type=ing"
    debug_info = {
        "steps": [],
        "errors": []
    }
    
    try:
        debug_info["steps"].append("요청 시작")
        # 헤더 설정
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # 목록 페이지 요청
        debug_info["steps"].append("목록 페이지 요청")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # HTML 파싱
        debug_info["steps"].append("HTML 파싱")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 첫 번째 전시회 찾기
        debug_info["steps"].append("첫 번째 전시회 찾기")
        first_exhibition = soup.select_one(".new_exh_list")
        
        if not first_exhibition:
            debug_info["errors"].append("전시회 목록을 찾을 수 없음")
            return {
                "error": "전시회 목록을 찾을 수 없습니다",
                "debug_info": debug_info,
                "crawled_at": datetime.now().isoformat(),
                "html_sample": soup.prettify()[:500]
            }
        
        # 기본 정보 추출
        debug_info["steps"].append("기본 정보 추출")
        title = ""
        location = ""
        date = ""
        image_url = ""
        detail_url = ""
        
        # 전시회 제목 추출
        try:
            # HTML 구조에 맞는 더 구체적인 선택자 사용
            title_div = soup.select_one('div[style*="width:1280px"][style*="text-align:center"][style*="font-size:26px"]')
            if title_div:
                title = title_div.text.strip()
            
            # 백업 방법: 첫 번째 테이블 앞에 있는 div 찾기
            if not title:
                first_table = soup.select_one("table")
                if first_table:
                    prev_divs = first_table.find_previous_siblings("div")
                    for div in prev_divs:
                        if "text-align:center" in div.get("style", "") and "font-size" in div.get("style", ""):
                            title = div.text.strip()
                            break
            
            # 공백 정리
            if title:
                title = ' '.join(title.split())
        except Exception as e:
            debug_info["errors"].append(f"제목 추출 중 오류: {str(e)}")
        
        # 장소
        location_elem = first_exhibition.select_one("span:nth-child(3)")
        if location_elem:
            location = location_elem.text.strip()
        
        # 기간
        date_elem = first_exhibition.select_one("span:nth-child(5)")
        if date_elem:
            date = date_elem.text.strip()
        
        # 이미지
        img_elem = first_exhibition.select_one("img")
        if img_elem:
            image_url = img_elem.get("src", "")
        
        # 상세 페이지 링크
        link_elem = first_exhibition.select_one("a")
        if link_elem:
            detail_url = link_elem.get("href", "")
            debug_info["detail_url_found"] = True
        else:
            debug_info["errors"].append("상세 페이지 링크를 찾을 수 없음")
        
        # 상세 정보 없으면 종료
        if not detail_url:
            debug_info["errors"].append("상세 페이지 URL이 없음")
            return {
                "error": "상세 페이지 URL을 찾을 수 없습니다",
                "debug_info": debug_info,
                "basic_info": {
                    "title": title,
                    "location": location,
                    "date": date,
                    "image_url": image_url
                },
                "crawled_at": datetime.now().isoformat()
            }
        
        # 상세 페이지 요청
        debug_info["steps"].append("상세 페이지 요청")
        detail_response = requests.get(detail_url, headers=headers)
        detail_response.raise_for_status()
        
        # 상세 페이지 HTML 파싱
        debug_info["steps"].append("상세 페이지 HTML 파싱")
        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
        
        # 상세 정보 추출
        debug_info["steps"].append("상세 정보 추출")
        
        # 설명/소개글
        description = ""
        desc_elem = detail_soup.select_one(".exhibition_info")
        if desc_elem:
            description = desc_elem.text.strip()
        else:
            # 대체 선택자 시도
            desc_elem = detail_soup.select_one(".info_text")
            if desc_elem:
                description = desc_elem.text.strip()
        
        # 가격 정보
        price = ""
        price_elem = detail_soup.select_one("th:-soup-contains('관람료') + td")
        if price_elem:
            price = price_elem.text.strip()
        
        # 운영 시간
        opening_hours = ""
        hours_elem = detail_soup.select_one("th:-soup-contains('운영시간') + td")
        if hours_elem:
            opening_hours = hours_elem.text.strip()
        
        # 휴관일
        closed_days = ""
        closed_elem = detail_soup.select_one("th:-soup-contains('휴관일') + td")
        if closed_elem:
            closed_days = closed_elem.text.strip()
        
        # 연락처
        contact = ""
        contact_elem = detail_soup.select_one("th:-soup-contains('문의') + td")
        if contact_elem:
            contact = contact_elem.text.strip()
        
        # 웹사이트
        website = ""
        website_elem = detail_soup.select_one("th:-soup-contains('홈페이지') + td a")
        if website_elem:
            website = website_elem.get("href", "")
        
        # 추가 이미지들
        additional_images = []
        img_elements = detail_soup.select(".detail_image img")
        for img in img_elements:
            img_url = img.get("src", "")
            if img_url and img_url != image_url:
                additional_images.append(img_url)
        
        # 메인 이미지
        main_image = ""
        try:
            # 첫 번째 방법: 스타일 속성으로 메인 이미지 찾기
            main_img = detail_soup.select_one('img[style*="max-width:100%"][style*="max-height:600px"]')
            if main_img:
                main_image = main_img.get("src", "")
            
            # 두 번째 방법: .detail_image 또는 .swiper-wrapper에서 이미지 찾기
            if not main_image:
                main_img = detail_soup.select_one(".swiper-wrapper img") or detail_soup.select_one(".detail_image img:first-child")
                if main_img:
                    main_image = main_img.get("src", "")
            
            # 세 번째 방법: 테이블 위에 있는 큰 이미지 찾기
            if not main_image:
                first_table = detail_soup.select_one("table")
                if first_table:
                    prev_imgs = first_table.find_previous_siblings("img")
                    if prev_imgs:
                        main_image = prev_imgs[0].get("src", "")
            
            # 네 번째 방법: style 속성이 있는 모든 img 태그 찾기
            if not main_image:
                styled_imgs = detail_soup.select('img[style]')
                for img in styled_imgs:
                    style = img.get("style", "")
                    if "max-width" in style or "width" in style or "height" in style:
                        main_image = img.get("src", "")
                        break
            
            # 상대 경로를 절대 경로로 변환
            if main_image and not main_image.startswith(('http://', 'https://')):
                main_image = f"https://art-map.co.kr{main_image}"
            
        except Exception as e:
            debug_info["errors"].append(f"메인 이미지 추출 중 오류: {str(e)}")
        
        # 결과 반환
        result = {
            "title": title,
            "location": location,
            "date": date,
            "image_url": image_url,
            "detail_url": detail_url,
            "description": description,
            "price": price,
            "opening_hours": opening_hours,
            "closed_days": closed_days,
            "contact": contact,
            "website": website,
            "additional_images": additional_images,
            "main_image": main_image,
            "crawled_at": datetime.now().isoformat()
        }
        
        return {
            "exhibition": result,
            "debug_info": debug_info
        }
        
    except Exception as e:
        import traceback
        debug_info["error"] = str(e)
        debug_info["traceback"] = traceback.format_exc()
        
        return {
            "error": str(e),
            "debug_info": debug_info,
            "crawled_at": datetime.now().isoformat()
        }

def crawl_exhibition_by_url(url):
    """아트맵에서 특정 URL의 전시회 정보를 크롤링"""
    debug_info = {
        "steps": [],
        "errors": []
    }
    
    try:
        debug_info["steps"].append("요청 시작")
        # 헤더 설정
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # 전시회 페이지 요청
        debug_info["steps"].append("전시회 페이지 요청")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # HTML 파싱
        debug_info["steps"].append("HTML 파싱")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 전시회 제목 추출
        title = ""
        try:
            # HTML 구조에 맞는 더 구체적인 선택자 사용
            title_div = soup.select_one('div[style*="width:1280px"][style*="text-align:center"][style*="font-size:26px"]')
            if title_div:
                title = title_div.text.strip()
            
            # 백업 방법: 첫 번째 테이블 앞에 있는 div 찾기
            if not title:
                first_table = soup.select_one("table")
                if first_table:
                    prev_divs = first_table.find_previous_siblings("div")
                    for div in prev_divs:
                        if "text-align:center" in div.get("style", "") and "font-size" in div.get("style", ""):
                            title = div.text.strip()
                            break
            
            # 공백 정리
            if title:
                title = ' '.join(title.split())
        except Exception as e:
            debug_info["errors"].append(f"제목 추출 중 오류: {str(e)}")
        
        # 기본 정보 테이블 찾기
        info_table = soup.select_one("table")
        if not info_table:
            debug_info["errors"].append("정보 테이블을 찾을 수 없음")
        
        # 전시 정보 추출
        period = ""
        time = ""
        place = ""
        address = ""
        closed_days = ""
        price = ""
        phone = ""
        website = ""
        artists = ""
        
        if info_table:
            # 기간
            period_row = info_table.select_one("th:-soup-contains('기간') ~ td")
            if period_row:
                period = period_row.text.strip()
            
            # 시간
            time_row = info_table.select_one("th:-soup-contains('시간') ~ td")
            if time_row:
                time = time_row.text.strip()
            
            # 장소
            place_row = info_table.select_one("th:-soup-contains('장소') ~ td")
            if place_row:
                place = place_row.text.strip()
                place_link = place_row.select_one("a")
                if place_link:
                    place = place_link.text.strip()
            
            # 주소
            addr_row = info_table.select_one("th:-soup-contains('주소') ~ td")
            if addr_row:
                address = addr_row.text.strip()
            
            # 휴관일
            closed_row = info_table.select_one("th:-soup-contains('휴관') ~ td")
            if closed_row:
                closed_days = closed_row.text.strip()
            
            # 관람료
            price_row = info_table.select_one("th:-soup-contains('관람료') ~ td")
            if price_row:
                price = price_row.text.strip()
            
            # 전화번호
            phone_row = info_table.select_one("th:-soup-contains('전화번호') ~ td")
            if phone_row:
                phone = phone_row.text.strip()
            
            # 웹사이트
            site_row = info_table.select_one("th:-soup-contains('사이트') ~ td")
            if site_row:
                site_link = site_row.select_one("a")
                if site_link:
                    website = site_link.get("href", "")
            
            # 작가
            artist_row = info_table.select_one("th:-soup-contains('작가') ~ td")
            if artist_row:
                artists = artist_row.text.strip()
        
        # 전시 설명 및 이미지
        description = ""
        desc_elem = soup.select_one(".exhibition_info")
        if desc_elem:
            description = desc_elem.text.strip()
        
        # 이미지들
        images = []
        img_elements = soup.select(".detail_image img")
        for img in img_elements:
            img_url = img.get("src", "")
            if img_url:
                images.append(img_url)
        
        # 메인 이미지
        main_image = ""
        try:
            # 첫 번째 방법: 스타일 속성으로 메인 이미지 찾기
            main_img = soup.select_one('img[style*="max-width:100%"][style*="max-height:600px"]')
            if main_img:
                main_image = main_img.get("src", "")
            
            # 두 번째 방법: .detail_image 또는 .swiper-wrapper에서 이미지 찾기
            if not main_image:
                main_img = soup.select_one(".swiper-wrapper img") or soup.select_one(".detail_image img:first-child")
                if main_img:
                    main_image = main_img.get("src", "")
            
            # 세 번째 방법: 테이블 위에 있는 큰 이미지 찾기
            if not main_image:
                first_table = soup.select_one("table")
                if first_table:
                    prev_imgs = first_table.find_previous_siblings("img")
                    if prev_imgs:
                        main_image = prev_imgs[0].get("src", "")
            
            # 네 번째 방법: style 속성이 있는 모든 img 태그 찾기
            if not main_image:
                styled_imgs = soup.select('img[style]')
                for img in styled_imgs:
                    style = img.get("style", "")
                    if "max-width" in style or "width" in style or "height" in style:
                        main_image = img.get("src", "")
                        break
            
            # 상대 경로를 절대 경로로 변환
            if main_image and not main_image.startswith(('http://', 'https://')):
                main_image = f"https://art-map.co.kr{main_image}"
            
        except Exception as e:
            debug_info["errors"].append(f"메인 이미지 추출 중 오류: {str(e)}")
        
        # 결과 반환
        result = {
            "title": title,
            "period": period,
            "opening_hours": time,
            "place": place,
            "address": address,
            "closed_days": closed_days,
            "price": price,
            "contact": phone,
            "website": website,
            "artists": artists,
            "description": description,
            "main_image": main_image,
            "additional_images": images,
            "source_url": url,
            "crawled_at": datetime.now().isoformat()
        }
        
        return {
            "exhibition": result,
            "debug_info": debug_info
        }
        
    except Exception as e:
        import traceback
        debug_info["error"] = str(e)
        debug_info["traceback"] = traceback.format_exc()
        
        return {
            "error": str(e),
            "debug_info": debug_info,
            "crawled_at": datetime.now().isoformat()
        }

def crawl_art_map_exhibitions_selenium():
    """셀레니움을 사용해 아트맵 현재 전시 목록 크롤링"""
    url = "https://art-map.co.kr/exhibition/new_list.php?cate=&od=2&area=&type=ing"
    debug_info = {
        "steps": [],
        "errors": []
    }
    driver = None
    
    try:
        debug_info["steps"].append("셀레니움 설정 시작")
        # 셀레니움 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 브라우저 창 숨기기
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 웹드라이버 초기화
        debug_info["steps"].append("웹드라이버 초기화")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # 페이지 로딩 대기
        debug_info["steps"].append("페이지 로딩 대기")
        time.sleep(5)  # 페이지가 완전히 로드될 때까지 대기
        
        # 전시회 항목 찾기
        debug_info["steps"].append("전시회 항목 찾기")
        exhibition_items = driver.find_elements(By.CLASS_NAME, "new_exh_list")
        
        if not exhibition_items:
            debug_info["errors"].append("전시회 항목을 찾을 수 없음")
            # 페이지 소스 캡처 (디버깅용)
            page_source = driver.page_source[:1000]  # 처음 1000자만 저장
            debug_info["page_source_sample"] = page_source
            driver.quit()
            
            return {
                "error": "전시회 목록을 찾을 수 없습니다",
                "debug_info": debug_info,
                "crawled_at": datetime.now().isoformat()
            }
        
        debug_info["steps"].append(f"전시회 항목 {len(exhibition_items)}개 발견")
        exhibitions = []
        
        # 처음 5개 항목만 처리 (테스트용)
        for idx, item in enumerate(exhibition_items[:5]):
            try:
                debug_info["steps"].append(f"항목 {idx+1} 처리 시작")
                
                # 항목 클릭하여 상세 페이지로 이동
                item.find_element(By.TAG_NAME, "a").click()
                debug_info["steps"].append(f"항목 {idx+1} 클릭")
                
                # 페이지 로딩 대기
                time.sleep(3)
                
                # 현재 URL 가져오기
                current_url = driver.current_url
                debug_info["steps"].append(f"항목 {idx+1} 상세 페이지 URL: {current_url}")
                
                # 상세 정보 크롤링
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # 전시회 제목 추출
                title = ""
                try:
                    # 여러 방법으로 제목 추출 시도
                    title_div = soup.select_one('div[style*="width:1280px"][style*="text-align:center"][style*="font-size:26px"]')
                    if title_div:
                        title = title_div.text.strip()
                    
                    # 백업 방법
                    if not title:
                        first_table = soup.select_one("table")
                        if first_table:
                            prev_divs = first_table.find_previous_siblings("div")
                            for div in prev_divs:
                                if div.get("style") and "text-align:center" in div.get("style") and "font-size" in div.get("style"):
                                    title = div.text.strip()
                                    break
                    
                    # 공백 정리
                    if title:
                        title = ' '.join(title.split())
                except Exception as e:
                    debug_info["errors"].append(f"항목 {idx+1} 제목 추출 오류: {str(e)}")
                
                # 기본 정보 테이블 찾기
                info_table = soup.select_one("table")
                
                # 전시 정보 추출
                period = ""
                time = ""
                place = ""
                address = ""
                closed_days = ""
                price = ""
                phone = ""
                website = ""
                artists = ""
                
                if info_table:
                    # 기간
                    period_row = info_table.select_one("th:-soup-contains('기간') ~ td")
                    if period_row:
                        period = period_row.text.strip()
                    
                    # 시간
                    time_row = info_table.select_one("th:-soup-contains('시간') ~ td")
                    if time_row:
                        time = time_row.text.strip()
                    
                    # 장소
                    place_row = info_table.select_one("th:-soup-contains('장소') ~ td")
                    if place_row:
                        place = place_row.text.strip()
                        place_link = place_row.select_one("a")
                        if place_link:
                            place = place_link.text.strip()
                    
                    # 주소
                    addr_row = info_table.select_one("th:-soup-contains('주소') ~ td")
                    if addr_row:
                        address = addr_row.text.strip()
                    
                    # 휴관일
                    closed_row = info_table.select_one("th:-soup-contains('휴관') ~ td")
                    if closed_row:
                        closed_days = closed_row.text.strip()
                    
                    # 관람료
                    price_row = info_table.select_one("th:-soup-contains('관람료') ~ td")
                    if price_row:
                        price = price_row.text.strip()
                    
                    # 전화번호
                    phone_row = info_table.select_one("th:-soup-contains('전화번호') ~ td")
                    if phone_row:
                        phone = phone_row.text.strip()
                    
                    # 웹사이트
                    site_row = info_table.select_one("th:-soup-contains('사이트') ~ td")
                    if site_row:
                        site_link = site_row.select_one("a")
                        if site_link:
                            website = site_link.get("href", "")
                    
                    # 작가
                    artist_row = info_table.select_one("th:-soup-contains('작가') ~ td")
                    if artist_row:
                        artists = artist_row.text.strip()
                
                # 설명
                description = ""
                desc_elem = soup.select_one(".exhibition_info")
                if desc_elem:
                    description = desc_elem.text.strip()
                
                # 메인 이미지
                main_image = ""
                try:
                    # 이미지 찾기
                    main_img = soup.select_one('img[style*="max-width:100%"][style*="max-height:600px"]')
                    if main_img:
                        main_image = main_img.get("src", "")
                    
                    # 다른 방법으로도 시도
                    if not main_image:
                        main_img = soup.select_one(".detail_image img")
                        if main_img:
                            main_image = main_img.get("src", "")
                    
                    # 상대 경로를 절대 경로로 변환
                    if main_image and not main_image.startswith(('http://', 'https://')):
                        main_image = f"https://art-map.co.kr{main_image}"
                    
                except Exception as e:
                    debug_info["errors"].append(f"항목 {idx+1} 이미지 추출 오류: {str(e)}")
                
                # 정보 저장
                exhibition_info = {
                    "title": title,
                    "period": period,
                    "opening_hours": time,
                    "place": place,
                    "address": address,
                    "closed_days": closed_days,
                    "price": price,
                    "contact": phone,
                    "website": website,
                    "artists": artists,
                    "description": description,
                    "main_image": main_image,
                    "source_url": current_url,
                    "crawled_at": datetime.now().isoformat()
                }
                
                exhibitions.append(exhibition_info)
                debug_info["steps"].append(f"항목 {idx+1} 정보 추출 성공")
                
                # 뒤로 가기
                driver.back()
                debug_info["steps"].append(f"항목 {idx+1} 처리 후 목록 페이지로 돌아감")
                
                # 페이지 로딩 대기
                time.sleep(3)
                
                # 새로운 항목 리스트 가져오기 (뒤로 가기 후 DOM이 새로 로드되기 때문)
                exhibition_items = driver.find_elements(By.CLASS_NAME, "new_exh_list")
                
            except Exception as e:
                debug_info["errors"].append(f"항목 {idx+1} 처리 중 오류: {str(e)}")
                # 오류가 발생해도 목록 페이지로 돌아가기
                driver.get(url)
                time.sleep(3)
                exhibition_items = driver.find_elements(By.CLASS_NAME, "new_exh_list")
        
        # 브라우저 종료
        driver.quit()
        
        return {
            "exhibitions": exhibitions,
            "total_count": len(exhibitions),
            "source_url": url,
            "crawled_at": datetime.now().isoformat(),
            "debug_info": debug_info
        }
        
    except Exception as e:
        debug_info["critical_error"] = str(e)
        import traceback
        debug_info["traceback"] = traceback.format_exc()
        
        # 드라이버 종료
        if driver:
            driver.quit()
        
        return {
            "error": str(e),
            "debug_info": debug_info,
            "crawled_at": datetime.now().isoformat()
        } 