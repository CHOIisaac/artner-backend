import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

class ChatGPTService:
    @staticmethod
    def get_response(query, context=None):
        """
        OpenAI API를 사용하여 사용자 질문에 대한 응답을 생성합니다.
        
        Args:
            query (str): 사용자의 질문
            context (str, optional): 추가적인 컨텍스트 정보
            
        Returns:
            str: OpenAI의 응답 텍스트
        """
        try:
            messages = [
                {"role": "system", "content": "당신은 미술 작품과 전시에 대해 친절하게 설명해주는 AI 도슨트입니다. 사용자가 작품, 작가, 미술 사조, 전시회 등에 대해 물어보면 자세히 답변해 주세요."}
            ]
            
            # 컨텍스트가 제공되면 추가
            if context:
                messages.append({"role": "system", "content": f"참고 정보: {context}"})
            
            # 사용자 질문 추가
            messages.append({"role": "user", "content": query})
            
            # API 호출
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message['content'].strip()
        
        except Exception as e:
            return f"죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다. {str(e)}" 