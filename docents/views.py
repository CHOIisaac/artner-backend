from django.shortcuts import render
from rest_framework import viewsets, filters, status, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
import base64

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.db import models, transaction
from rest_framework.response import Response

from docents.models import Folder, Docent
from docents.serializers import (
    FolderSerializer, DocentDetailSerializer, 
    DocentCreateSerializer, DocentSerializer, FolderDetailSerializer
)
from docents.services import DocentService


# Create your views here.
@extend_schema_view(
    list=extend_schema(
        summary="폴더 목록 조회",
        tags=["Folders"]
    ),
    retrieve=extend_schema(
        summary="폴더 상세 조회 (포함된 도슨트들과 함께)",
        tags=["Folders"]
    ),
    create=extend_schema(
        summary="폴더 생성",
        tags=["Folders"]
    ),
    partial_update=extend_schema(
        summary="폴더 부분 수정",
        tags=["Folders"]
    ),
    destroy=extend_schema(
        summary="폴더 삭제",
        tags=["Folders"]
    ),
)
class FolderViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """저장 폴더 관리 ViewSet"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """액션에 따라 적절한 시리얼라이저 반환"""
        if self.action == 'retrieve':
            return FolderDetailSerializer
        return FolderSerializer

    def get_queryset(self):
        """현재 사용자의 폴더만 조회"""
        return Folder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """폴더 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)


@extend_schema_view(
    retrieve=extend_schema(
        summary="도슨트 상세 조회",
        tags=["Docents"]
    ),
    status=extend_schema(
        summary="저장 상태 확인",
        parameters=[
            OpenApiParameter(name='item_type', description='항목 유형 (artist, artwork)', required=True, type=str),
            OpenApiParameter(name='title', description='제목(작가명 또는 작품명)', required=True, type=str)
        ],
        tags=["Docents"]
    ),
    toggle=extend_schema(
        summary="도슨트 저장/삭제 토글",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'folder_id': {'type': 'integer', 'description': '폴더 ID'},
                    'item_type': {'type': 'string', 'enum': ['artist', 'artwork'], 'description': '항목 유형'},
                    'title': {'type': 'string', 'description': '제목(작가명 또는 작품명)'},
                    'life_period': {'type': 'string', 'description': '생애기간 (작가인 경우)'},
                    'artist_name': {'type': 'string', 'description': '작가명 (작품인 경우)'},
                    'script': {'type': 'string', 'description': '도슨트 스크립트'},
                    'notes': {'type': 'string', 'description': '메모'},
                    'thumbnail': {'type': 'string', 'format': 'binary', 'description': '썸네일 이미지'}
                },
                'required': ['folder_id', 'item_type', 'title']
            }
        },
        responses={
            200: {"description": "도슨트 삭제 성공"},
            201: {"description": "도슨트 저장 성공"},
            400: {"description": "잘못된 요청"},
            404: {"description": "폴더를 찾을 수 없음"}
        },
        tags=["Docents"]
    )
)
class DocentViewSet(mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """도슨트 관리 ViewSet (개별 조회 및 액션만 지원)"""
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """요청 메서드에 따라 적절한 시리얼라이저 반환"""
        if self.action == 'create':
            return DocentCreateSerializer
        elif self.action in ['retrieve']:
            return DocentDetailSerializer
        return DocentSerializer

    def get_queryset(self):
        """현재 사용자의 도슨트만 조회"""
        return Docent.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """도슨트 저장 상태 확인"""
        item_type = request.query_params.get('item_type')
        title = request.query_params.get('title')

        if not item_type or not title:
            return Response(
                {"error": "item_type과 title 쿼리 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 해당 항목이 저장된 폴더 목록 확인
        saved_docents = Docent.objects.filter(
            user=request.user,
            item_type=item_type,
            title=title
        )

        folders = []
        for docent in saved_docents:
            folders.append({
                'id': docent.folder.id,
                'name': docent.folder.name
            })

        return Response({
            'is_saved': len(folders) > 0,
            'folders': folders
        })

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """도슨트 저장/삭제 토글"""
        folder_id = request.data.get('folder_id')
        item_type = request.data.get('item_type')
        title = request.data.get('title')

        # 추가 데이터
        life_period = request.data.get('life_period', '')
        artist_name = request.data.get('artist_name', '')
        script = request.data.get('script', '')  # 도슨트 스크립트 추가
        notes = request.data.get('notes', '')
        thumbnail = request.data.get('thumbnail')

        # 필수 파라미터 확인
        if not all([folder_id, item_type, title]):
            return Response(
                {"error": "folder_id, item_type, title이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 폴더 확인
        try:
            folder = Folder.objects.get(id=folder_id, user=request.user)
        except Folder.DoesNotExist:
            return Response(
                {"error": "해당 ID의 폴더가 존재하지 않거나 접근 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 트랜잭션으로 저장/삭제 처리
        with transaction.atomic():
            # 이미 저장된 도슨트인지 확인
            try:
                docent = Docent.objects.get(
                    user=request.user,
                    folder=folder,
                    item_type=item_type,
                    title=title
                )
                # 이미 존재하면 삭제
                docent.delete()
                return Response(
                    {"message": "항목이 폴더에서 삭제되었습니다."},
                    status=status.HTTP_200_OK
                )

            except Docent.DoesNotExist:
                # 존재하지 않으면 생성
                docent = Docent.objects.create(
                    user=request.user,
                    folder=folder,
                    item_type=item_type,
                    title=title,
                    life_period=life_period,
                    artist_name=artist_name,
                    script=script,  # 도슨트 스크립트 저장
                    notes=notes,
                    thumbnail=thumbnail
                )
                return Response({
                    "message": "항목이 폴더에 저장되었습니다.",
                    'item': DocentDetailSerializer(docent).data
                }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="실시간 도슨트 스크립트 생성",
    description="텍스트 또는 이미지 기반으로 도슨트 스크립트를 빠르게 생성합니다. 음성은 백그라운드에서 생성됩니다.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'prompt_text': {'type': 'string', 'description': '커스텀 프롬프트 텍스트 (선택사항)'},
                'prompt_image': {'type': 'string', 'description': '이미지 URL (선택사항)'},
                'artist_name': {'type': 'string', 'description': '아티스트 이름 (텍스트 모드용, 선택사항)'},
                'item_type': {'type': 'string', 'enum': ['artist', 'artwork'], 'description': '항목 유형 (기본값: artist)'},
                'item_name': {'type': 'string', 'description': '항목명 (선택사항)'}
            }
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'text': {'type': 'string', 'description': '도슨트 스크립트'},
                'item_type': {'type': 'string', 'description': '항목 유형'},
                'item_name': {'type': 'string', 'description': '항목명'},
                'audio_job_id': {'type': 'string', 'description': '음성 생성 작업 ID'}
            }
        },
        400: {'description': '잘못된 요청'},
        500: {'description': '서버 오류'}
    },
    tags=["Docents"]
)
@api_view(['POST'])
def generate_realtime_docent(request):
    """실시간 도슨트 스크립트 생성 API (음성은 백그라운드)"""
    try:
        import asyncio
        
        docent_service = DocentService()
        
        # 새 이벤트 루프 생성 및 비동기 함수 실행
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        result = loop.run_until_complete(
            docent_service.generate_realtime_docent(
                prompt_text=request.data.get('prompt_text'),
                prompt_image=request.data.get('prompt_image'),
                artist_name=request.data.get('artist_name'),
                item_type=request.data.get('item_type', 'artist'),
                item_name=request.data.get('item_name')
            )
        )
        
        return Response(result, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="음성 생성 상태 조회",
    description="백그라운드에서 생성 중인 음성의 상태를 조회하고, 완료 시 직접 재생 가능한 URL을 제공합니다.",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'job_id': {'type': 'string', 'description': '작업 ID'},
                'status': {'type': 'string', 'enum': ['pending', 'processing', 'completed', 'failed'], 'description': '작업 상태'},
                'audio_url': {'type': 'string', 'description': '스웨거에서 직접 재생 가능한 음성 URL (완료시)'},
                'audio_base64': {'type': 'string', 'description': 'Base64 인코딩된 음성 데이터 (완료시)'},
                'timestamps': {'type': 'array', 'description': '문장별 타임스탬프 (완료시)'},
                'error': {'type': 'string', 'description': '에러 메시지 (실패시)'}
            }
        },
        404: {'description': '작업을 찾을 수 없음'}
    },
    tags=["Docents"]
)
@api_view(['GET'])
def get_audio_status(request, job_id):
    """음성 생성 상태 조회 API"""
    try:
        from .tasks import audio_job_manager
        job_status = audio_job_manager.get_job_status(job_id)
        
        if not job_status:
            return Response(
                {'error': '작업을 찾을 수 없습니다.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 완료된 경우 스트리밍 URL 추가
        if job_status['status'] == 'completed' and job_status['audio_base64']:
            audio_url = request.build_absolute_uri(f'/api/docents/audio/{job_id}/stream/')
            job_status['audio_url'] = audio_url
        
        return Response(job_status, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="음성 파일 스트리밍",
    description="완성된 음성을 MP3 파일로 스트리밍합니다. 스웨거에서 직접 재생 가능합니다.",
    responses={
        200: {
            'description': 'MP3 오디오 파일',
            'content': {
                'audio/mpeg': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },
        404: {'description': '작업을 찾을 수 없거나 아직 완료되지 않음'}
    },
    tags=["Docents"]
)
@api_view(['GET'])
def stream_audio(request, job_id):
    """음성 파일 스트리밍 API (스웨거에서 직접 재생 가능)"""
    try:
        from .tasks import audio_job_manager
        import base64
        from django.http import HttpResponse
        
        job_status = audio_job_manager.get_job_status(job_id)
        
        if not job_status:
            return HttpResponse('작업을 찾을 수 없습니다.', status=404)
        
        if job_status['status'] != 'completed':
            return HttpResponse(f'음성 생성이 아직 완료되지 않았습니다. 상태: {job_status["status"]}', status=404)
        
        if not job_status['audio_base64']:
            return HttpResponse('음성 데이터가 없습니다.', status=404)
        
        # Base64를 바이너리로 변환
        audio_data = base64.b64decode(job_status['audio_base64'])
        
        # MP3 파일로 응답
        response = HttpResponse(audio_data, content_type='audio/mpeg')
        response['Content-Disposition'] = f'inline; filename="docent_{job_id}.mp3"'
        response['Content-Length'] = len(audio_data)
        
        return response
        
    except Exception as e:
        return HttpResponse(f'오류: {str(e)}', status=500)