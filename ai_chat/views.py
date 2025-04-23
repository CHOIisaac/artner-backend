from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from .serializers import ChatQuerySerializer, ChatResponseSerializer
from artworks.models import Artwork
from exhibitions.models import Exhibition
from .services import ChatGPTService

class ChatView(APIView):
    """
    채팅 쿼리를 처리하고 응답을 반환하는 간단한 API 뷰
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChatQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        
        # 관련 작품 및 전시 검색
        artworks = Artwork.objects.filter(
            Q(title__icontains=query) | 
            Q(artist__name__icontains=query) |
            Q(description__icontains=query)
        )[:3]
        
        exhibitions = Exhibition.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )[:2]
        
        # 컨텍스트 정보 구성
        context = None
        if artworks.exists() or exhibitions.exists():
            context = ""
            if artworks.exists():
                context += "관련 작품 정보:\n"
                for artwork in artworks:
                    context += f"- {artwork.title}: 작가 {artwork.artist.name}, {artwork.created_year}년, {artwork.description[:200]}...\n"
            
            if exhibitions.exists():
                context += "관련 전시 정보:\n"
                for exhibition in exhibitions:
                    context += f"- {exhibition.title}: {exhibition.description[:200]}...\n"
        
        # ChatGPT 응답 가져오기
        response_text = ChatGPTService.get_response(query, context)
        
        # 관련 작품/전시
        related_artwork = artworks.first() if artworks.exists() else None
        related_exhibition = exhibitions.first() if exhibitions.exists() else None
        
        # 선택적으로 로그 저장 (필요한 경우)
        # ChatLog.objects.create(query=query, response=response_text)
        
        # 응답 데이터 구성
        response_data = {
            'query': query,
            'response': response_text,
            'related_artwork': related_artwork,
            'related_exhibition': related_exhibition
        }
        
        return Response(response_data)

class ArtworkInfoView(APIView):
    """
    특정 작품에 대한 정보를 제공하는 API 뷰
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        artwork_id = request.data.get('artwork_id')
        
        if not artwork_id:
            return Response({"error": "artwork_id는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            artwork = Artwork.objects.get(id=artwork_id)
            
            # 작품 정보 응답 생성
            query = f"{artwork.title}에 대해 알려주세요."
            response_text = f"🖼️ {artwork.title}\n"
            response_text += f"작가: {artwork.artist.name}, {artwork.created_year}년\n"
            response_text += f"재료: {artwork.medium}\n\n"
            response_text += f"{artwork.description}\n\n"
            
            # 연관된 도슨트 확인
            from docents.models import Docent
            docents = Docent.objects.filter(items__artwork=artwork).distinct()
            if docents.exists():
                response_text += "📝 이 작품에 대한 오디오 도슨트가 있습니다. '도슨트 듣기'를 선택하세요."
            
            response_data = {
                'query': query,
                'response': response_text,
                'related_artwork': artwork,
                'related_exhibition': None
            }
            
            return Response(response_data)
            
        except Artwork.DoesNotExist:
            return Response({"error": "해당 작품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
