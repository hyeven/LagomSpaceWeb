# 확장 모듈(예: SQLAlchemy, Flask-Login)을 초기화합니다.

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
