from rest_framework import viewsets, filters, status, mixins
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.db import transaction
from rest_framework.response import Response

from docents.models import Folder, Docent
from docents.serializers import (
    FolderSerializer, DocentDetailSerializer, 
    DocentCreateSerializer, DocentSerializer, FolderDetailSerializer
)
from docents.services import DocentService
from docents.tasks import audio_job_manager


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
        """현재 사용자의 폴더만 조회 - 성능 최적화 적용"""
        queryset = Folder.objects.filter(user=self.request.user)
        
        # 액션별 최적화
        if self.action == 'retrieve':
            # 상세 조회 시 관련 도슨트들을 함께 조회
            queryset = queryset.prefetch_related('docents')
        elif self.action == 'list':
            # 목록 조회 시 도슨트 개수만 필요하므로 count 최적화
            from django.db.models import Count
            queryset = queryset.annotate(items_count=Count('docents'))
        
        return queryset

    def perform_create(self, serializer):
        """폴더 생성 시 현재 사용자 정보 자동 저장"""
        serializer.save(user=self.request.user)


@extend_schema_view(
    retrieve=extend_schema(
        summary="저장된 도슨트 상세 조회",
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
    description="텍스트 또는 이미지 중 하나를 입력받아 도슨트 스크립트를 생성합니다. LLM이 자동으로 작가/작품을 판별하고 적절한 도슨트를 생성하며, 음성은 백그라운드에서 생성됩니다.",
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'input_text': {'type': 'string', 'description': '텍스트 입력 (작가명, 작품명 등)'},
                'input_image': {'type': 'string', 'description': '이미지 URL'},
                'input_image_file': {'type': 'string', 'format': 'binary', 'description': '이미지 파일 (모바일 카메라 촬영)'}
            },
            'oneOf': [
                {
                    'properties': {'input_text': {'type': 'string'}},
                    'required': ['input_text'],
                    'description': '텍스트 기반 도슨트 생성'
                },
                {
                    'properties': {'input_image': {'type': 'string'}},
                    'required': ['input_image'], 
                    'description': '이미지 URL 기반 도슨트 생성'
                },
                {
                    'properties': {'input_image_file': {'type': 'string', 'format': 'binary'}},
                    'required': ['input_image_file'], 
                    'description': '이미지 파일 기반 도슨트 생성 (모바일 카메라)'
                }
            ]
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'text': {'type': 'string', 'description': '도슨트 스크립트'},
                'item_type': {'type': 'string', 'description': 'LLM이 판별한 항목 유형 (artist/artwork)'},
                'item_name': {'type': 'string', 'description': 'LLM이 정확히 식별한 항목명'},
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
    """
    실시간 도슨트 스크립트 생성 API
    
    텍스트, 이미지 URL, 또는 이미지 파일 중 하나를 입력받아:
    1. LLM이 입력값이 작가인지 작품인지 자동 판별
    2. 해당 타입에 맞는 도슨트 스크립트 생성
    3. 음성은 백그라운드에서 별도 처리
    """
    try:
        import asyncio
        import logging
        import base64
        
        logger = logging.getLogger(__name__)
        
        # 요청 데이터 확인
        input_text = request.data.get('input_text')
        input_image = request.data.get('input_image')  # URL
        input_image_file = request.FILES.get('input_image_file')  # 업로드된 파일
        
        print(f"🎯 API 호출됨!")
        print(f"📝 input_text: {input_text}")
        print(f"🖼️ input_image: {input_image}")
        print(f"📁 input_image_file: {input_image_file}")
        
        # 세 개 중 하나는 반드시 있어야 함
        if not input_text and not input_image and not input_image_file:
            return Response(
                {'error': 'input_text, input_image, input_image_file 중 하나는 필수입니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 이미지 파일이 있는 경우 base64로 인코딩
        processed_image = None
        if input_image_file:
            try:
                # 이미지 파일을 base64로 인코딩
                image_data = input_image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
                # MIME 타입 확인
                content_type = input_image_file.content_type or 'image/jpeg'
                processed_image = f"data:{content_type};base64,{image_base64}"
                print(f"🔄 이미지 파일을 base64로 변환 완료 (크기: {len(image_data)} 바이트)")
                
            except Exception as e:
                print(f"❌ 이미지 파일 처리 실패: {e}")
                return Response(
                    {'error': f'이미지 파일 처리 실패: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif input_image:
            processed_image = input_image
        
        try:
            docent_service = DocentService()
            print("✅ DocentService 초기화 성공")
        except Exception as e:
            print(f"❌ DocentService 초기화 실패: {e}")
            return Response(
                {'error': f'서비스 초기화 실패: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 새 이벤트 루프 생성 및 비동기 함수 실행
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        print("🔄 비동기 함수 실행 시작...")
        
        try:
            result = loop.run_until_complete(
                docent_service.generate_realtime_docent(
                    prompt_text=input_text,
                    prompt_image=processed_image,  # URL 또는 base64 데이터
                )
            )
            print(f"✅ 비동기 함수 실행 완료")
            print(f"📝 결과 text 길이: {len(result.get('text', ''))}")
            print(f"🎨 결과 item_type: {result.get('item_type')}")
            print(f"📛 결과 item_name: {result.get('item_name')}")
        except Exception as e:
            print(f"❌ 비동기 함수 실행 실패: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'도슨트 생성 실패: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # LLM 판별 결과 로깅
        logger.info(f"🤖 LLM 판별 완료: {result['item_type']} '{result['item_name']}'")
        
        return Response(result, status=status.HTTP_200_OK)
        
    except ValueError as e:
        logger.error(f"❌ 도슨트 생성 실패 (잘못된 요청): {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"💥 도슨트 생성 실패 (서버 오류): {str(e)}")
        import traceback
        traceback.print_exc()
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


@extend_schema(
    summary="디버깅: 메모리 작업 현황 조회",
    description="현재 메모리에 저장된 음성 생성 작업들의 상태를 조회합니다. (개발용)",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'total_jobs': {'type': 'integer', 'description': '총 작업 수'},
                'jobs': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'job_id': {'type': 'string'},
                            'status': {'type': 'string'},
                            'created_at': {'type': 'string'},
                            'age_minutes': {'type': 'integer', 'description': '생성 후 경과 시간(분)'},
                            'script_preview': {'type': 'string', 'description': '스크립트 미리보기 (50자)'}
                        }
                    }
                }
            }
        }
    },
    tags=["Debug"]
)
@api_view(['GET'])
def debug_memory_jobs(request):
    """메모리에 저장된 작업들의 현황 조회 (디버깅용)"""
    from datetime import datetime
    
    jobs_info = []
    with audio_job_manager.lock:
        for job_id, job in audio_job_manager.jobs.items():
            age_minutes = int((datetime.now() - job['created_at']).total_seconds() / 60)
            script_preview = job['script_text'][:50] + '...' if len(job['script_text']) > 50 else job['script_text']
            
            jobs_info.append({
                'job_id': job_id,
                'status': job['status'],
                'created_at': job['created_at'].isoformat(),
                'age_minutes': age_minutes,
                'script_preview': script_preview
            })
    
    # 생성 시간 순으로 정렬 (최신 먼저)
    jobs_info.sort(key=lambda x: x['created_at'], reverse=True)
    
    return Response({
        'total_jobs': len(jobs_info),
        'jobs': jobs_info
    })