import os
import json
import base64
import httpx
from datetime import datetime
from django.core.files.base import ContentFile
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import openai
import boto3

from .models import DocentScript


class DocentService:
    """도슨트 생성 서비스"""
    
    def __init__(self):
        # OpenAI 설정
        self.chat_model = ChatOpenAI(model="gpt-4v")
        self.tts_model = "tts-1-hd"
        self.tts_voice = "alloy"
        self.tts_speed = 1.0
        
        # AWS Polly 설정
        self.polly = boto3.client(
            "polly",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name="ap-northeast-2"
        )
    
    def create_docent(self, item_type: str, item_name: str, item_info: str, 
                     prompt_text: str, prompt_image: str) -> DocentScript:
        """도슨트 생성"""
        # 1. 도슨트 스크립트 객체 생성
        docent = DocentScript.objects.create(
            item_type=item_type,
            item_name=item_name,
            item_info=item_info,
            prompt_text=prompt_text,
            prompt_image=prompt_image
        )
        
        try:
            # 2. 이미지 다운로드 및 인코딩
            image_data = base64.b64encode(
                httpx.get(prompt_image).content
            ).decode("utf-8")
            
            # 3. GPT-4V로 도슨트 스크립트 생성
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    }
                ]
            )
            chat_response = self.chat_model.invoke([message])
            docent.llm_response = chat_response.content
            
            # 4. OpenAI TTS로 음성 생성
            tts_response = openai.audio.speech.create(
                model=self.tts_model,
                voice=self.tts_voice,
                speed=self.tts_speed,
                input=chat_response.content
            )
            
            # OpenAI 음성 파일 저장
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            openai_filename = f"openai-{current_time}.mp3"
            docent.openai_audio.save(
                openai_filename,
                ContentFile(tts_response.content)
            )
            
            # 5. Amazon Polly로 음성 및 타임스탬프 생성
            polly_response = self.polly.synthesize_speech(
                Text=chat_response.content,
                OutputFormat='mp3',
                VoiceId='Seoyeon'
            )
            
            # Polly 음성 파일 저장
            polly_filename = f"polly-{current_time}.mp3"
            docent.polly_audio.save(
                polly_filename,
                ContentFile(polly_response["AudioStream"].read())
            )
            
            # 타임스탬프 생성
            marks_response = self.polly.synthesize_speech(
                Text=chat_response.content,
                OutputFormat='json',
                VoiceId='Seoyeon',
                SpeechMarkTypes=['sentence']
            )
            
            # 타임스탬프 저장
            marks_raw = marks_response["AudioStream"].read().decode("utf-8").splitlines()
            docent.timestamps = [json.loads(line) for line in marks_raw]
            
            docent.save()
            return docent
            
        except Exception as e:
            # 에러 발생 시 생성된 객체 삭제
            docent.delete()
            raise e 

    async def generate_realtime_docent(self, artist_name: str) -> dict:
        """실시간 도슨트 생성
        
        Args:
            artist_name: 아티스트 이름
            
        Returns:
            dict: {
                'text': 도슨트 스크립트 텍스트,
                'audio_base64': base64로 인코딩된 음성 데이터,
                'timestamps': 문장 타임스탬프
            }
        """
        try:
            # 1. GPT-4로 도슨트 스크립트 생성
            prompt = f"{artist_name}에 대해 도슨트처럼 설명해주세요. 작품 설명과 역사적 맥락을 포함해주세요."
            message = HumanMessage(content=prompt)
            chat_response = self.chat_model.invoke([message])
            script_text = chat_response.content
            
            # 2. OpenAI TTS로 음성 생성
            tts_response = openai.audio.speech.create(
                model=self.tts_model,
                voice=self.tts_voice,
                speed=self.tts_speed,
                input=script_text
            )
            
            # 음성 데이터를 base64로 인코딩
            audio_base64 = base64.b64encode(tts_response.content).decode('utf-8')
            
            # 3. Amazon Polly로 타임스탬프 생성
            marks_response = self.polly.synthesize_speech(
                Text=script_text,
                OutputFormat='json',
                VoiceId='Seoyeon',
                SpeechMarkTypes=['sentence']
            )
            
            # 타임스탬프 파싱
            marks_raw = marks_response["AudioStream"].read().decode("utf-8").splitlines()
            timestamps = [json.loads(line) for line in marks_raw]
            
            return {
                'text': script_text,
                'audio_base64': audio_base64,
                'timestamps': timestamps
            }
            
        except Exception as e:
            raise e 