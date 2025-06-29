import json
import base64
import httpx
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import boto3
from decouple import config
from django.db.models import Q
from artists.models import Artist
from artworks.models import Artwork


class DocentService:
    """도슨트 생성 서비스"""
    
    def __init__(self):
        # OpenAI 설정 (decouple로 환경 변수 가져오기)
        openai_api_key = config('OPENAI_API_KEY', default='')
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일에 설정해주세요.")
            
        openai_model = config('OPENAI_MODEL', default='gpt-4')
        
        self.chat_model = ChatOpenAI(
            model=openai_model,
            api_key=openai_api_key
        )
        
        # AWS Polly 설정 (음성 생성 및 타임스탬프)
        aws_access_key = config('AWS_ACCESS_KEY_ID', default='')
        aws_secret_key = config('AWS_SECRET_ACCESS_KEY', default='')
        aws_region = config('AWS_REGION', default='ap-northeast-2')

        if not aws_access_key or not aws_secret_key:
            raise ValueError("AWS 자격 증명이 설정되지 않았습니다. .env 파일에 설정해주세요.")

        self.polly = boto3.client(
            "polly",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
    
    def _unified_search(self, query: str) -> dict:
        """통합 검색: 작가와 작품을 모두 검색하고 가장 적합한 결과 반환"""
        # 작가 검색 (이름, 대표작으로 검색)
        artists = Artist.objects.filter(
            Q(title__icontains=query) | 
            Q(representative_work__icontains=query)
        ).values('id', 'title', 'life_period', 'representative_work')
        
        # 작품 검색 (제목, 작가명으로 검색)
        artworks = Artwork.objects.filter(
            Q(title__icontains=query) | 
            Q(artist_name__icontains=query)
        ).values('id', 'title', 'artist_name', 'created_year')
        
        # 결과 정리 및 우선순위 결정
        results = []
        
        # 작가 결과 추가 (정확도 점수 계산)
        for artist in artists:
            accuracy = self._calculate_accuracy(query, artist['title'])
            results.append({
                'type': 'artist',
                'id': artist['id'],
                'name': artist['title'],
                'accuracy': accuracy,
                'metadata': {
                    'life_period': artist.get('life_period', ''),
                    'representative_work': artist.get('representative_work', '')
                }
            })
        
        # 작품 결과 추가 (정확도 점수 계산)
        for artwork in artworks:
            accuracy = self._calculate_accuracy(query, artwork['title'])
            results.append({
                'type': 'artwork',
                'id': artwork['id'],
                'name': artwork['title'],
                'accuracy': accuracy,
                'metadata': {
                    'artist_name': artwork.get('artist_name', ''),
                    'created_year': artwork.get('created_year', '')
                }
            })
        
        # 정확도 순으로 정렬
        results.sort(key=lambda x: x['accuracy'], reverse=True)
        
        if results:
            # 가장 정확도가 높은 결과 반환
            best_match = results[0]
            return {
                'found': True,
                'item_type': best_match['type'],
                'item_name': best_match['name'],
                'item_id': best_match['id'],
                'accuracy': best_match['accuracy'],
                'metadata': best_match['metadata'],
                'all_results': results[:3]  # 상위 3개 결과도 함께 반환
            }
        else:
            # 검색 결과 없음
            return {
                'found': False,
                'item_type': 'artist',  # 기본값
                'item_name': query,
                'item_id': None,
                'accuracy': 0.0,
                'metadata': {},
                'all_results': []
            }
    
    def _calculate_accuracy(self, query: str, target: str) -> float:
        """검색어와 대상 문자열 간의 정확도 계산"""
        query_lower = query.lower().strip()
        target_lower = target.lower().strip()
        
        # 완전 일치
        if query_lower == target_lower:
            return 1.0
        
        # 포함 관계
        if query_lower in target_lower:
            return 0.8
            
        if target_lower in query_lower:
            return 0.7
        
        # 부분 매칭 (간단한 유사도)
        common_chars = set(query_lower) & set(target_lower)
        if common_chars:
            similarity = len(common_chars) / max(len(query_lower), len(target_lower))
            return similarity * 0.5
        
        return 0.0
    
    def _build_prompt(self, prompt_text: str, search_result: dict) -> str:
        """프롬프트 생성 (검색 결과 반영)"""
        if prompt_text:
            return prompt_text
            
        if not search_result.get('item_name'):
            raise ValueError("검색 결과가 없습니다.")
        
        item_name = search_result['item_name']
        item_type = search_result['item_type']
        metadata = search_result.get('metadata', {})
        
        # 메타데이터 정보 구성
        meta_info = ""
        if search_result['found'] and metadata:
            if item_type == 'artist':
                life_period = metadata.get('life_period', '')
                representative_work = metadata.get('representative_work', '')
                if life_period or representative_work:
                    meta_info = f"\n\n참고 정보:\n"
                    if life_period:
                        meta_info += f"- 생애: {life_period}\n"
                    if representative_work:
                        meta_info += f"- 대표작: {representative_work}"
            else:  # artwork
                artist_name = metadata.get('artist_name', '')
                created_year = metadata.get('created_year', '')
                if artist_name or created_year:
                    meta_info = f"\n\n참고 정보:\n"
                    if artist_name:
                        meta_info += f"- 작가: {artist_name}\n"
                    if created_year:
                        meta_info += f"- 제작년도: {created_year}"
        
        if item_type == 'artist':
            return f"""
            당신은 전문 미술관 도슨트입니다. {item_name} 작가에 대해 관람객들에게 설명해주세요.
            
            다음 내용을 포함해서 자연스럽고 흥미로운 도슨트를 제공해주세요:
            1. 작가의 생애와 배경
            2. 주요 작품과 특징
            3. 예술사적 의미
            4. 흥미로운 일화나 사실
            
            3-4분 정도 길이로, 마치 실제 미술관에서 설명하는 것처럼 친근하고 교육적인 톤으로 작성해주세요.{meta_info}
            """
        else:  # artwork
            return f"""
            당신은 전문 미술관 도슨트입니다. '{item_name}' 작품에 대해 관람객들에게 설명해주세요.
            
            다음 내용을 포함해서 자연스럽고 흥미로운 도슨트를 제공해주세요:
            1. 작품의 기본 정보 (제작 시기, 기법 등)
            2. 작품의 주제와 의미
            3. 시각적 특징과 기법
            4. 역사적/문화적 배경
            5. 감상 포인트
            
            3-4분 정도 길이로, 마치 실제 미술관에서 설명하는 것처럼 친근하고 교육적인 톤으로 작성해주세요.{meta_info}
            """
    
    async def _generate_script(self, prompt: str, prompt_image: str = None) -> str:
        """GPT를 이용한 도슨트 스크립트 생성"""
        if prompt_image:
            # URL 형식 검증 및 수정
            if not prompt_image.startswith(('http://', 'https://')):
                if prompt_image.startswith('//'):
                    prompt_image = 'https:' + prompt_image
                elif prompt_image.startswith('/'):
                    # 상대 경로인 경우 기본 도메인 추가 (필요시 수정)
                    prompt_image = 'https://example.com' + prompt_image
                else:
                    # 프로토콜이 없는 경우 https 추가
                    prompt_image = 'https://' + prompt_image
            
            # 이미지가 있는 경우 - GPT-4V 사용
            try:
                async with httpx.AsyncClient() as client:
                    image_response = await client.get(prompt_image)
                    if image_response.status_code != 200:
                        raise ValueError(f"이미지를 가져올 수 없습니다. 상태 코드: {image_response.status_code}")
                    image_data = base64.b64encode(image_response.content).decode("utf-8")
            except httpx.RequestError as e:
                raise ValueError(f"이미지 URL에 접근할 수 없습니다: {prompt_image}. 에러: {str(e)}")
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    }
                ]
            )
        else:
            # 텍스트만 있는 경우 - GPT-4 사용
            message = HumanMessage(content=prompt)
        
        chat_response = self.chat_model.invoke([message])
        return chat_response.content
    
    def _generate_audio_and_timestamps(self, script_text: str) -> tuple[str, list]:
        """Amazon Polly를 이용한 음성 및 타임스탬프 생성"""
        # 음성 생성
        polly_response = self.polly.synthesize_speech(
            Text=script_text,
            OutputFormat='mp3',
            VoiceId='Seoyeon'
        )
        audio_base64 = base64.b64encode(polly_response["AudioStream"].read()).decode('utf-8')
        
        # 타임스탬프 생성
        marks_response = self.polly.synthesize_speech(
            Text=script_text,
            OutputFormat='json',
            VoiceId='Seoyeon',
            SpeechMarkTypes=['sentence']
        )
        
        marks_raw = marks_response["AudioStream"].read().decode("utf-8").splitlines()
        timestamps = [json.loads(line) for line in marks_raw]
        
        return audio_base64, timestamps
    
    async def generate_realtime_docent(
        self, 
        prompt_text: str = None,
        prompt_image: str = None,
        artist_name: str = None,
        item_type: str = 'artist',
        item_name: str = None
    ) -> dict:
        """실시간 도슨트 스크립트 생성 (통합 검색 기반)"""
        try:
            search_result = None
            final_item_type = item_type
            final_item_name = item_name or artist_name or "알 수 없음"
            
            # 1. 통합 검색 수행 (prompt_text가 없고 artist_name이 있는 경우)
            if not prompt_text and artist_name:
                search_result = self._unified_search(artist_name)
                
                # 검색 결과 적용
                if search_result['found']:
                    final_item_type = search_result['item_type']
                    final_item_name = search_result['item_name']
                    
                print(f"🔍 검색 결과: {search_result}")  # 디버깅용
            
            # 2. 프롬프트 생성
            if prompt_text:
                final_prompt = prompt_text
            else:
                final_prompt = self._build_prompt(prompt_text, search_result or {
                    'item_name': final_item_name,
                    'item_type': final_item_type,
                    'found': False,
                    'metadata': {}
                })
            
            # 3. 도슨트 스크립트 생성 (빠른 응답)
            script_text = await self._generate_script(final_prompt, prompt_image)
            
            # 4. 백그라운드 음성 생성 작업 시작
            from .tasks import audio_job_manager
            audio_job_id = audio_job_manager.create_job(script_text)
            
            response = {
                'text': script_text,
                'item_type': final_item_type,
                'item_name': final_item_name,
                'audio_job_id': audio_job_id
            }
            
            # 검색 정보도 함께 반환
            if search_result:
                response['search_info'] = {
                    'found_in_db': search_result['found'],
                    'accuracy': search_result.get('accuracy', 0.0),
                    'item_id': search_result.get('item_id'),
                    'metadata': search_result.get('metadata', {}),
                    'alternative_results': search_result.get('all_results', [])
                }
            
            return response
            
        except Exception as e:
            raise e