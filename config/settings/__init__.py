from .base import *

# 개발 환경에서는 development.py 설정 로드
# 운영 환경에서는 production.py 설정 로드
# 환경 변수로 구분 가능
import os
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .development import * 