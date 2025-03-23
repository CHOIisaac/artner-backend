from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class TimeStampedModel(models.Model):
    """생성 및 수정 시간을 자동으로 기록하는 추상 모델"""
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)

    class Meta:
        abstract = True


class Tag(TimeStampedModel):
    """태그 모델"""
    name = models.CharField(_('이름'), max_length=50, unique=True)

    class Meta:
        verbose_name = _('태그')
        verbose_name_plural = _('태그 목록')

    def __str__(self):
        return self.name


class Review(TimeStampedModel):
    """리뷰 모델"""
    content = models.TextField(_('내용'))
    rating = models.PositiveSmallIntegerField(_('평점'), default=5)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('작성자')
    )
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        verbose_name=_('컨텐츠 타입')
    )
    object_id = models.PositiveIntegerField(_('객체 ID'))

    class Meta:
        verbose_name = _('리뷰')
        verbose_name_plural = _('리뷰 목록')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.user.username}의 리뷰 - {self.rating}점"


class PublishableModel(TimeStampedModel):
    """공개 여부를 설정할 수 있는 추상 모델"""
    is_public = models.BooleanField(_('공개 여부'), default=True)

    class Meta:
        abstract = True

    def publish(self):
        self.is_public = True
        self.save()

    def unpublish(self):
        self.is_public = False
        self.save()


class NamedModel(TimeStampedModel):
    """이름과 설명을 가진 추상 모델"""
    title = models.CharField(_('제목'), max_length=200)
    description = models.TextField(_('설명'), blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
