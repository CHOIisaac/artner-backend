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
    
    def _search_in_database(self, query: str) -> dict:
        """데이터베이스에서 작가/작품 검색"""
        # 작가 검색 (이름, 대표작으로 검색)
        artists = Artist.objects.filter(
            Q(title__icontains=query) | 
            Q(representative_work__icontains=query)
        ).values('id', 'title', 'life_period', 'representative_work')[:5]
        
        # 작품 검색 (제목, 작가명으로 검색)
        artworks = Artwork.objects.filter(
            Q(title__icontains=query) | 
            Q(artist_name__icontains=query)
        ).values('id', 'title', 'artist_name', 'created_year')[:5]
        
        return {
            'artists': list(artists),
            'artworks': list(artworks)
        }
    
    async def _classify_with_ai(self, user_input: str, db_results: dict) -> dict:
        """AI를 이용한 작가/작품 분류 및 정보 추출"""
        classification_prompt = f"""
        사용자가 "{user_input}"라고 입력했습니다.
        
        데이터베이스 검색 결과:
        작가들: {db_results['artists']}
        작품들: {db_results['artworks']}
        
        다음 규칙에 따라 분류해주세요:
        1. 검색 결과에서 가장 일치하는 항목을 찾아주세요
        2. 없다면 일반적인 미술 지식으로 작가인지 작품인지 판단해주세요
        3. 반드시 JSON 형식으로 응답해주세요
        
        응답 형식:
        {{
            "item_type": "artist" 또는 "artwork",
            "item_name": "최종 확정된 이름",
            "confidence": 0.0~1.0 사이의 확신도,
            "matched_db_item": 데이터베이스에서 찾은 경우 해당 객체, 없으면 null,
            "reasoning": "판단 근거"
        }}
        
        예시:
        - "고흐" → {{"item_type": "artist", "item_name": "빈센트 반 고흐", "confidence": 0.9}}
        - "별이 빛나는 밤" → {{"item_type": "artwork", "item_name": "별이 빛나는 밤", "confidence": 0.9}}
        """
        
        message = HumanMessage(content=classification_prompt)
        response = self.chat_model.invoke([message])
        
        try:
            # JSON 응답 파싱
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # JSON 형식이 아닌 경우 기본값 반환
                return {
                    "item_type": "artist",
                    "item_name": user_input,
                    "confidence": 0.5,
                    "matched_db_item": None,
                    "reasoning": "JSON 파싱 실패로 기본값 사용"
                }
        except json.JSONDecodeError:
            return {
                "item_type": "artist",
                "item_name": user_input,
                "confidence": 0.5,
                "matched_db_item": None,
                "reasoning": "JSON 파싱 오류로 기본값 사용"
            }
    
    def _build_prompt(self, prompt_text: str, artist_name: str, item_type: str, classification_result: dict = None) -> str:
        """프롬프트 생성 (분류 결과 반영)"""
        if prompt_text:
            return prompt_text
            
        if not artist_name:
            raise ValueError("prompt_text 또는 artist_name 중 하나는 필수입니다.")
        
        # 분류 결과가 있으면 더 정확한 정보 사용
        final_name = classification_result.get('item_name', artist_name) if classification_result else artist_name
        final_type = classification_result.get('item_type', item_type) if classification_result else item_type
        
        # 데이터베이스 정보 활용
        db_info = ""
        if classification_result and classification_result.get('matched_db_item'):
            db_item = classification_result['matched_db_item']
            if final_type == 'artist':
                db_info = f"\n\n참고 정보:\n- 생애: {db_item.get('life_period', '')}\n- 대표작: {db_item.get('representative_work', '')}"
            else:  # artwork
                db_info = f"\n\n참고 정보:\n- 작가: {db_item.get('artist_name', '')}\n- 제작년도: {db_item.get('created_year', '')}"
        
        if final_type == 'artist':
            return f"""
            당신은 전문 미술관 도슨트입니다. {final_name} 작가에 대해 관람객들에게 설명해주세요.
            
            다음 내용을 포함해서 자연스럽고 흥미로운 도슨트를 제공해주세요:
            1. 작가의 생애와 배경
            2. 주요 작품과 특징
            3. 예술사적 의미
            4. 흥미로운 일화나 사실
            
            3-4분 정도 길이로, 마치 실제 미술관에서 설명하는 것처럼 친근하고 교육적인 톤으로 작성해주세요.{db_info}
            """
        else:  # artwork
            return f"""
            당신은 전문 미술관 도슨트입니다. '{final_name}' 작품에 대해 관람객들에게 설명해주세요.
            
            다음 내용을 포함해서 자연스럽고 흥미로운 도슨트를 제공해주세요:
            1. 작품의 기본 정보 (제작 시기, 기법 등)
            2. 작품의 주제와 의미
            3. 시각적 특징과 기법
            4. 역사적/문화적 배경
            5. 감상 포인트
            
            3-4분 정도 길이로, 마치 실제 미술관에서 설명하는 것처럼 친근하고 교육적인 톤으로 작성해주세요.{db_info}
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
        """실시간 도슨트 스크립트 생성 (음성은 백그라운드)"""
        try:
            classification_result = None
            final_item_type = item_type
            final_item_name = item_name or artist_name or "알 수 없음"
            
            # 1. 스마트 분류 수행 (prompt_text가 없고 artist_name이 있는 경우)
            if not prompt_text and artist_name:
                # 데이터베이스 검색
                db_results = self._search_in_database(artist_name)
                
                # AI 분류
                classification_result = await self._classify_with_ai(artist_name, db_results)
                
                # 분류 결과 적용
                final_item_type = classification_result.get('item_type', item_type)
                final_item_name = classification_result.get('item_name', final_item_name)
                
                print(f"🤖 AI 분류 결과: {classification_result}")  # 디버깅용
            
            # 2. 프롬프트 생성
            final_prompt = self._build_prompt(prompt_text, artist_name, final_item_type, classification_result)
            
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
            
            # 분류 정보도 함께 반환 (선택사항)
            if classification_result:
                response['classification_info'] = {
                    'confidence': classification_result.get('confidence', 0.5),
                    'reasoning': classification_result.get('reasoning', ''),
                    'found_in_db': classification_result.get('matched_db_item') is not None
                }
            
            return response
            
        except Exception as e:
            raise e