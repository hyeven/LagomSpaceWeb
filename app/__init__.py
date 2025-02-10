# Flask 애플리케이션을 초기화하고 블루프린트와 확장을 등록하는 파일입니다.
# 애플리케이션 팩토리 패턴을 사용하여 여러 환경에서 앱을 생성할 수 있게 합니다.
# 앱 생성 → 설정 → 확장 초기화 → 블루프린트 등록

import os
import sqlite3
from flask import Flask, g
from .database import get_db, close_db
from .extensions import db, login_manager
from .models import User
from .routes import main
from .routes import auth  # auth 블루프린트 임포트
from flask_wtf.csrf import CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")  # config.py 불러와서 적용
    
    # teardown_appcontext 등록
    app.teardown_appcontext(close_db)

    # 확장 모듈 초기화
    db.init_app(app)  # SQLAlchemy와 Flask 앱 인스턴스 연결 과정
    login_manager.init_app(app)  # login_manager : 세션관리, 접근제한, 리디렉션 기능 탑재

    # 로그인 뷰 설정 (로그인하지 않은 사용자가 보호된 페이지에 접근했을 때 리디렉션할 라우트를 지정)
    login_manager.login_view = ("auth.login")  # 'main'은 블루프린트 이름, 'login'은 함수 이름


    # 블루프린트 등록
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    # flask-login 확장에서 사용자 세션 관리하기 위해서 필요한 함수, create_app 안에 있어야 함
    @login_manager.user_loader 
    def load_user(user_id):
        return User.query.get(int(user_id))  # 사용자 ID로 User 객체 로드
    
    return app


