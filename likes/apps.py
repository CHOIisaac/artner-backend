from django.apps import AppConfig


class LikesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'likes'
    verbose_name = '좋아요 관리'
