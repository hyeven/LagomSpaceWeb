import sqlite3
from flask import g

DATABASE = r"C:\Projects\LagomSpaceWeb\instance\site.db"

# 데이터베이스 연결 함수
def get_db():
    if "db" not in g:
        print("Opening a new database connection...")

        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

# 데이터베이스 연결 해제 함수
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
