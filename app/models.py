# 데이터베이스 모델을 정의하는 파일입니다.
# 사용자, 게시글, 댓글 등의 데이터베이스 테이블 구조를 설계.
# SQLite와 SQLAlchemy를 사용해 테이블과 데이터 구조를 설계합니다.

# NOTE
# User 모델이 Flask-Login과 호환되기 위해 **UserMixin**을 상속받아야 합니다.
# UserMixin은 is_authenticated, is_active 등의 기본 메서드를 제공합니다.

"""
Flask 셸(power shell)에서 다음 명령어로 데이터베이스 테이블을 생성

flask shell
>>> from app import db, create_app
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()

"""

from flask_login import UserMixin
from .extensions import db
from datetime import datetime
from zoneinfo import ZoneInfo #python 3.9이상


class User(db.Model, UserMixin):
    # 데이터베이스에 생성될 테이블정의(userlist)
    __tablename__ = "userlist"

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 자동 증가
    user_id = db.Column(db.String(50), nullable=False, unique=True)  # 사용자 고유 ID
    user_name = db.Column(db.String(80), nullable=False, unique=True)
    user_passwd = db.Column(db.String(128), nullable=False)
    user_email = db.Column(db.String(120), nullable=False, unique=True)
    last_updated = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(ZoneInfo('Asia/Seoul')))  # 최종수정일

    def get_id(self):
        return str(self.idx)  # 'idx'를 반환하도록 get_id() 메서드 재정의

    # 객체 출력, 디버깅할 때 여기서 정의된 문자열 반환
    def __repr__(self):
        return f"<User user_id={self.user_id}>"
    
    
    
    
class Board(db.Model):
    __tablename__ = "boardlist"

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 자동 증가
    board_title = db.Column(db.String(255), nullable=False) # 제목은 최대 255자
    board_content = db.Column(db.Text, nullable=False) # 내용은 길이 제한 없음
    user_id = db.Column(db.String(50), nullable=False)  # 사용자 고유 ID
    user_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S"))
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S"))
    view_count = db.Column(db.Integer, default=0)  # 조회수 컬럼 추가
    file_path = db.Column(db.Text, nullable=True)  # 파일 경로 추가


    def __repr__(self):
        return f"<boardlist {self.board_title}>"
