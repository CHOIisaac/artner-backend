from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class TimeStampedModel(models.Model):
    """생성 및 수정 시간을 자동으로 기록하는 추상 모델"""
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)

    class Meta:
        abstract = True


class PublishableModel(TimeStampedModel):
    """공개 여부를 설정할 수 있는 추상 모델"""
    is_public = models.BooleanField(_('공개 여부'), default=True)
    published_at = models.DateTimeField(_('공개 시간'), null=True, blank=True)

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


class FeaturedModel(TimeStampedModel):
    is_featured = models.BooleanField(_('주요 항목 여부'), default=False)
    
    class Meta:
        abstract = True