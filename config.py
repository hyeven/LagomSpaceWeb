"""
- 애플리케이션의 **설정 파일**입니다.
- 데이터베이스 연결 문자열, 비밀 키, 디버그 설정 등의 환경 설정을 정의합니다.

SECRET_KEY = 'your_secret_key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///community.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False


"""

import os


# Secret key for session management and CSRF protection
SECRET_KEY = os.urandom(24)

# SQLite 데이터베이스 설정
SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "connect_args": {"timeout": 15}  # 데이터베이스 타임아웃을 15초로 설정
}

# CSRF 보호 설정
WTF_CSRF_ENABLED = False

# 세션 쿠키의 지속 시간을 명시적으로 설정하여 만료 문제를 방지
# PERMANENT_SESSION_LIFETIME = timedelta(days=1)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# 업로드 폴더가 없으면 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Flask 설정
class Config:
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 파일 크기 제한: 16MB
    
    # 설정 추가
    # SQLALCHEMY_DATABASE_URI = "sqlite:///C:\Projects\LagomSpaceWeb\instance\site.db"
    # # C:\Projects\LagomSpaceWeb\instance\site.db
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True  # SQLAlchemy 쿼리 로그 활성화