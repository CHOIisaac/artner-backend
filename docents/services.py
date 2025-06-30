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
        # OpenAI 설정
        openai_api_key = config('OPENAI_API_KEY', default='')
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
            
        self.chat_model = ChatOpenAI(
            model=config('OPENAI_MODEL', default='gpt-4'),
            api_key=openai_api_key
        )
        
        # AWS Polly 설정
        aws_access_key = config('AWS_ACCESS_KEY_ID', default='')
        aws_secret_key = config('AWS_SECRET_ACCESS_KEY', default='')
        aws_region = config('AWS_REGION', default='ap-northeast-2')

        if not aws_access_key or not aws_secret_key:
            raise ValueError("AWS 자격 증명이 설정되지 않았습니다.")

        self.polly = boto3.client(
            "polly",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

    async def generate_realtime_docent(
        self, 
        prompt_text: str = None,
        prompt_image: str = None,
        artist_name: str = None,
        item_type: str = 'artist',
        item_name: str = None
    ) -> dict:
        """실시간 도슨트 스크립트 생성"""
        try:
            print(f"🎯 API 호출됨!")
            print(f"📝 prompt_text: {prompt_text}")
            print(f"🎨 artist_name: {artist_name}")
            print(f"🖼️ prompt_image: {prompt_image}")
            
            # 입력값 결정
            if prompt_text:
                query = prompt_text
                use_image = False
            elif prompt_image:
                query = "이미지를 분석해서 도슨트를 생성해주세요"
                use_image = True
            else:
                query = artist_name or item_name or "알 수 없음"
                use_image = False
                
            print(f"🔍 최종 query: {query}")
            print(f"🖼️ 이미지 사용: {use_image}")
            
            print("🤖 LLM으로 도슨트 생성 시작...")
            
            # 통합 프롬프트 - 타입 판별과 도슨트 생성을 한 번에
            unified_prompt = f"""
            당신은 전문 미술관 도슨트입니다.

            입력: "{query}"

            먼저 이것이 작가명인지 작품명인지 판별하고, 그에 맞는 3-4분 분량의 상세한 도슨트를 작성해주세요.

            **응답 형식을 반드시 지켜주세요:**
            
            TYPE: artist (또는 artwork)
            
            [도슨트 내용]

            **작가인 경우 (TYPE: artist):**
            - 작가의 생애와 배경
            - 주요 작품과 특징  
            - 예술사적 의미
            - 흥미로운 일화나 사실

            **작품인 경우 (TYPE: artwork):**
            - 작품의 기본 정보 (제작 시기, 기법 등)
            - 작품의 주제와 의미
            - 시각적 특징과 기법
            - 역사적/문화적 배경
            - 감상 포인트

            친근하고 교육적인 톤으로, 마치 실제 미술관에서 설명하는 것처럼 작성해주세요.
            반드시 첫 줄에 "TYPE: artist" 또는 "TYPE: artwork"를 명시하고, 그 다음 줄부터 도슨트 내용을 작성해주세요.
            """
            
            print(f"📤 LLM에 전송할 프롬프트: {unified_prompt}...")
            
            if use_image and prompt_image:
                # 이미지가 있는 경우 GPT-4V 사용
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": unified_prompt + "\n\n제공된 이미지도 함께 분석해서 더 정확한 설명을 해주세요."},
                        {
                            "type": "image_url",
                            "image_url": {"url": prompt_image}
                        }
                    ]
                )
            else:
                # 텍스트만 있는 경우
                message = HumanMessage(content=unified_prompt)
            
            response = self.chat_model.invoke([message])
            full_response = response.content
            
            print(f"📥 LLM 응답 받음!")
            print(f"📏 전체 응답 길이: {len(full_response)}")
            print(f"📄 응답 미리보기: {full_response[:200]}...")
            
            # 타입 파싱
            lines = full_response.split('\n')
            final_item_type = "artist"  # 기본값
            script_text = full_response  # 기본값
            
            for i, line in enumerate(lines):
                if line.strip().startswith('TYPE:'):
                    type_part = line.strip().replace('TYPE:', '').strip().lower()
                    if 'artwork' in type_part:
                        final_item_type = "artwork"
                    elif 'artist' in type_part:
                        final_item_type = "artist"
                    
                    # TYPE 라인 이후의 내용을 스크립트로 사용
                    script_text = '\n'.join(lines[i+1:]).strip()
                    break
            
            print(f"🎨 파싱된 타입: {final_item_type}")
            print(f"📄 최종 스크립트 미리보기: {script_text[:100]}...")
            
            print(f"🎨 최종 타입: {final_item_type}")
            
            # 음성 생성 작업 시작
            from .tasks import audio_job_manager
            audio_job_id = audio_job_manager.create_job(script_text)
            print(f"🔊 음성 작업 ID: {audio_job_id}")
            
            result = {
                'text': script_text,
                'item_type': final_item_type,
                'item_name': query,
                'audio_job_id': audio_job_id
            }
            
            print(f"✅ 최종 결과 반환!")
            return result
            
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            import traceback
            traceback.print_exc()
            raise e

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