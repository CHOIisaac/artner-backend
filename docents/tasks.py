import asyncio
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
import threading
from .services import DocentService


class AudioJobManager:
    """인메모리 음성 생성 작업 관리자"""
    
    def __init__(self):
        self.jobs: Dict[str, dict] = {}
        self.lock = threading.Lock()
    
    def create_job(self, script_text: str) -> str:
        """새 음성 생성 작업 생성"""
        job_id = str(uuid.uuid4())
        
        with self.lock:
            self.jobs[job_id] = {
                'status': 'pending',
                'script_text': script_text,
                'created_at': datetime.now(),
                'audio_base64': None,
                'timestamps': None,
                'error': None
            }
        
        # 백그라운드에서 음성 생성 시작
        thread = threading.Thread(target=self._generate_audio_sync, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """작업 상태 조회"""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
                
            # 1시간 이상 된 작업은 삭제
            if datetime.now() - job['created_at'] > timedelta(hours=1):
                del self.jobs[job_id]
                return None
                
            return {
                'job_id': job_id,
                'status': job['status'],
                'audio_base64': job['audio_base64'],
                'timestamps': job['timestamps'],
                'error': job['error']
            }
    
    def _generate_audio_sync(self, job_id: str):
        """음성 생성 (별도 스레드에서 실행)"""
        try:
            with self.lock:
                job = self.jobs.get(job_id)
                if not job:
                    return
                
                self.jobs[job_id]['status'] = 'processing'
            
            # 도슨트 서비스로 음성 생성
            docent_service = DocentService()
            audio_base64, timestamps = docent_service._generate_audio_and_timestamps(
                job['script_text']
            )
            
            with self.lock:
                if job_id in self.jobs:
                    self.jobs[job_id].update({
                        'status': 'completed',
                        'audio_base64': audio_base64,
                        'timestamps': timestamps
                    })
                    
        except Exception as e:
            with self.lock:
                if job_id in self.jobs:
                    self.jobs[job_id].update({
                        'status': 'failed',
                        'error': str(e)
                    })


# 전역 작업 관리자 인스턴스
audio_job_manager = AudioJobManager() 