import json
import base64
import httpx
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import boto3
from decouple import config


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
    
    def _build_prompt(self, prompt_text: str, artist_name: str, item_type: str) -> str:
        """프롬프트 생성"""
        if prompt_text:
            return prompt_text
            
        if not artist_name:
            raise ValueError("prompt_text 또는 artist_name 중 하나는 필수입니다.")
        
        if item_type == 'artist':
            return f"""
            당신은 전문 미술관 도슨트입니다. {artist_name} 작가에 대해 관람객들에게 설명해주세요.
            
            다음 내용을 포함해서 자연스럽고 흥미로운 도슨트를 제공해주세요:
            1. 작가의 생애와 배경
            2. 주요 작품과 특징
            3. 예술사적 의미
            4. 흥미로운 일화나 사실
            
            3-4분 정도 길이로, 마치 실제 미술관에서 설명하는 것처럼 친근하고 교육적인 톤으로 작성해주세요.
            """
        else:  # artwork
            return f"""
            당신은 전문 미술관 도슨트입니다. '{artist_name}' 작품에 대해 관람객들에게 설명해주세요.
            
            다음 내용을 포함해서 자연스럽고 흥미로운 도슨트를 제공해주세요:
            1. 작품의 기본 정보 (제작 시기, 기법 등)
            2. 작품의 주제와 의미
            3. 시각적 특징과 기법
            4. 역사적/문화적 배경
            5. 감상 포인트
            
            3-4분 정도 길이로, 마치 실제 미술관에서 설명하는 것처럼 친근하고 교육적인 톤으로 작성해주세요.
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
            # 1. 프롬프트 생성
            final_prompt = self._build_prompt(prompt_text, artist_name, item_type)
            
            # 2. 도슨트 스크립트 생성 (빠른 응답)
            script_text = await self._generate_script(final_prompt, prompt_image)
            
            # 3. 최종 항목명 결정
            final_item_name = item_name or artist_name or "알 수 없음"
            
            # 4. 백그라운드 음성 생성 작업 시작
            from .tasks import audio_job_manager
            audio_job_id = audio_job_manager.create_job(script_text)
            
            return {
                'text': script_text,
                'item_type': item_type,
                'item_name': final_item_name,
                'audio_job_id': audio_job_id
            }
            
        except Exception as e:
            raise e