from django.db import models
from django.core.exceptions import ValidationError


class Highlight(models.Model):
    """
    LLM 응답에서 하이라이트(밑줄)된 텍스트를 저장하는 모델
    """
    # 외래 키 관계 (작가 또는 작품)
    artist = models.ForeignKey('artists.Artist', null=True, blank=True, on_delete=models.CASCADE,
                              related_name='highlighted_texts', verbose_name='작가')
    artwork = models.ForeignKey('artworks.Artwork', null=True, blank=True, on_delete=models.CASCADE,
                               related_name='highlighted_texts', verbose_name='작품')
    
    # 하이라이트된 텍스트
    text = models.TextField(verbose_name='하이라이트된 텍스트')
    
    # 전체 응답 내에서의 위치 정보 (인덱스)
    start_index = models.PositiveIntegerField(verbose_name='시작 인덱스')
    end_index = models.PositiveIntegerField(verbose_name='종료 인덱스')
    
    # 하이라이트가 속한 LLM 응답 (전체 컨텍스트)
    llm_response = models.TextField(verbose_name='LLM 전체 응답')
    
    # 생성 시간
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    
    class Meta:
        ordering = ['start_index']
        verbose_name = '하이라이트된 텍스트'
        verbose_name_plural = '하이라이트된 텍스트'
        
    def clean(self):
        """
        작가와 작품 중 하나만 선택되었는지 검증합니다.
        """
        if bool(self.artist) == bool(self.artwork):
            raise ValidationError("작가 또는 작품 중 하나만 선택해야 합니다.")
            
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    @property
    def content_object(self):
        """
        연결된 객체(작가 또는 작품)를 반환합니다.
        """
        return self.artist or self.artwork
    
    @property
    def content_type_str(self):
        """
        콘텐츠 타입 문자열을 반환합니다.
        """
        if self.artist:
            return 'artist'
        elif self.artwork:
            return 'artwork'
        return None
        
    def __str__(self):
        return self.text[:50] + ('...' if len(self.text) > 50 else '')
