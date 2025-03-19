from django.apps import AppConfig


class ArtsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'arts'
    verbose_name = '아트너'

    def ready(self):
        # 시그널 등록
        import arts.signals 