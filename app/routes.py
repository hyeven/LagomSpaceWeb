# URL 라우팅과 뷰 함수를 정의합니다.
# 각 경로에 대한 처리 로직을 담고 있습니다.
# Blueprint를 사용해 라우트들을 모듈화하고 깔끔하게 관리합니다.

import os
import time

from app import get_db
from os.path import basename
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, send_from_directory
from flask_wtf import FlaskForm
from .database import get_db
from .models import User, Board
from .extensions import db
from .forms import SignUpForm, LoginForm, MyPageForm, BoardCreateForm, BoardUpdateForm
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import text




# Blueprint 생성
main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

# 관리자 페이지
@main.route("/adminpage", methods=["GET", "POST"])
@login_required
def admin_page():
    # user_id가 'admin'인 경우만 접근 허용
    if current_user.user_id != "admin":
        abort(403)  # 접근 거부 (403 Forbidden)
        
    # 모든 사용자 정보 조회
    users = User.query.all()
    
    # POST 요청 처리 (삭제 또는 수정)
    if request.method == "POST":
        user_id = request.form.get("user_id")
        action = request.form.get("action")

        if action == "delete":
            # 사용자 삭제
            user = User.query.filter_by(user_id=user_id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                flash(f"User {user_id} deleted successfully.", "success")
            else:
                flash("User not found.", "danger")
        elif action == "update":
            # 사용자 정보 수정
            user = User.query.filter_by(user_id=user_id).first()
            if user:
                new_name = request.form.get("new_name")
                new_email = request.form.get("new_email")
                user.user_name = new_name
                user.user_email = new_email
                db.session.commit()
                flash(f"User {user_id} updated successfully.", "success")
            else:
                flash("User not found.", "danger")

        return redirect(url_for("main.admin_page"))
    
    # 관리자 전용 페이지 렌더링
    return render_template("admin_page.html", users=users)

# 에러 핸들러 추가
@main.app_errorhandler(403)
def forbidden_error(error):
    return render_template("403.html"), 403

# CSRF 보호를 위한 빈 폼
class DummyForm(FlaskForm):
    pass  

# About 라우트 추가
@main.route("/about")
def about():
    return render_template("about.html")

# Blueprint 생성
auth = Blueprint("auth", __name__)


# 회원가입 라우트 추가
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()  # forms.py에 정의된 객체 생성
    show_modal = False
    if form.validate_on_submit():  # POST 요청이면서 폼의 유효성 검사가 통과된 경우 True를 반환 (필수필드확인, 비밀번호확인)
        try:
            hashed_password = generate_password_hash(form.user_passwd.data)  # 비밀번호 해싱
            new_user = User(  # models.py에 정의된 새로운 사용자 객체 생성
                user_id=form.user_id.data,
                user_name=form.user_name.data,
                user_email=form.user_email.data,
                user_passwd=hashed_password,
                last_updated=datetime.now(ZoneInfo("Asia/Seoul")),
            )
            db.session.add(new_user)  # DB에 추가
            db.session.commit()  # DB에 저장
            flash("Account created successfully!", "success",)
            
            show_modal = True
            print("show_modal:", show_modal)
            print("welcome new user ::: ")
            print("new user id ::: ", form.user_id.data)
            print("new user email ::: ", form.user_email.data)

            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()  # 롤백 처리
            flash("An error occurred: " + str(e), "danger")
        finally:
            db.session.close()  # 세션 종료
    return render_template('signup.html', form=form, show_modal=show_modal)


# 로그인 라우트
@auth.route("/login",  methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit(): # **form.validate_on_submit()**는 POST 요청에서만 실행되어야 합니다.
        user = User.query.filter_by(user_id=form.user_id.data).first()
        print("User found:", user)  # 사용자 객체가 제대로 조회되었는지 확인
        
        if user and check_password_hash(user.user_passwd, form.user_passwd.data):
            print("Password check: Success")  # 비밀번호 검증 성공 여부 확인
            login_user(user)
            print("User logged in:", current_user)  # 로그인 상태 확인
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.index"))  # 로그인 후 메인 페이지로 이동
        else:
            print("Invalid login attempt")  # 로그인 실패 확인
            flash("Invalid user ID or password.", "danger")
    elif request.method == "POST":
        print("Form validation failed")  # 폼 검증 실패 확인
        print("Form data:", form.data)
        print("Form errors:", form.errors)
    return render_template("login.html", form=form)


# 로그아웃 라우트
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))

# 프로필
@main.route("/profile")
@login_required
def profile():
    print("Current user:", current_user)
    return f"Hello, {current_user.user_id}!"

# 마이페이지 조회
@main.route("/mypage", methods=["GET"])
@login_required
def mypage():
    form = MyPageForm(obj=current_user)  # 현재 사용자 데이터를 폼에 로드
    
    form.user_name.data = current_user.user_name
    form.user_email.data = current_user.user_email
    form.user_passwd.data = "********"  # 비밀번호 필드를 '********'로 초기화
    last_updated = current_user.last_updated.strftime("%Y-%m-%d %H:%M:%S")  

    return render_template("mypage.html", form=form, last_updated=last_updated)

# 마이페이지 수정 폼 로드
@main.route("/mypage/update", methods=["GET"])
@login_required
def mypage_update():
    form = MyPageForm(obj=current_user) # 현재 사용자 데이터를 로드
    last_updated = current_user.last_updated.strftime("%Y-%m-%d %H:%M:%S")  
    
    return render_template("mypage_update.html", form=form, last_updated=last_updated)


# 마이페이지 수정 요청 확인
@main.route("/mypage/update", methods=["POST"])
@login_required
def mypage_update_save():
    form = MyPageForm(obj=current_user) # 현재 사용자 데이터를 로드
    
    if form.validate_on_submit():
        current_user.user_id = form.user_id.data
        current_user.user_name = form.user_name.data
        current_user.user_email = form.user_email.data
        current_user.last_updated = datetime.now(ZoneInfo("Asia/Seoul"))
        
        # 비밀번호가 입력되었을 때만 업데이트
        if form.user_passwd.data.strip():  # 비밀번호 입력이 비어 있지 않은 경우
            current_user.user_passwd = generate_password_hash(form.user_passwd.data)

        try:
            db.session.commit()
            flash("Your information has been updated.", "success")
            
            print("mypage updated ::: ")
            print("mypage updated user_id ::: ", form.user_id.data)
            print("mypage updated user_name::: ", form.user_name.data)
            print("mypage updated user_email ::: ", form.user_email.data)

            
            return redirect(url_for("main.mypage"))  # 수정 후 마이페이지로 이동
        except Exception as e:
            db.session.rollback()
            flash("An error occurred: " + str(e), "danger")
    else:
        flash("Form validation failed. Please check your input.", "danger")
        
    # 폼 데이터를 다시 로드하여 템플릿에 전달
    last_updated = current_user.last_updated.strftime("%Y-%m-%d %H:%M:%S")
    return render_template("mypage_update.html", form=form, last_updated=last_updated)    
        
# 게시판 목록 조회 / 검색 기능
@main.route("/board", methods=["GET"])
@login_required
def board():
    # from .models import Board (상단에 기재)
    page = request.args.get("page", 1, type=int)  # 기본 페이지는 1
    per_page = 10  # 페이지당 항목 수
    offset = (page - 1) * per_page  # OFFSET 계산
    
    search_query = request.args.get("search", "")  # 검색어
    filter_by = request.args.get("filter", "")  # 검색 필터 (user_name, user_id, Date)
    
    # 기본 쿼리
    base_query = "SELECT * FROM boardlist"
    count_query = "SELECT COUNT(*) AS total FROM boardlist"
        
    # 검색 조건 추가
    params = []  # 기본적으로 빈 매개변수 리스트

    if search_query:
        if filter_by == "user_name":
            base_query += " WHERE user_name LIKE ?"
            count_query += " WHERE user_name LIKE ?"
            params.append(f"%{search_query}%")
        elif filter_by == "user_id":
            base_query += " WHERE user_id LIKE ?"
            count_query += " WHERE user_id LIKE ?"
            params.append(f"%{search_query}%")
        elif filter_by == "Date":
            base_query += " WHERE DATE(created_at) = ?"
            count_query += " WHERE DATE(created_at) = ?"
            params.append(search_query)
        else:
            base_query += " WHERE board_title LIKE ? OR board_content LIKE ?"
            count_query += " WHERE board_title LIKE ? OR board_content LIKE ?"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
    

    # 정렬 및 페이징 처리
    base_query += " ORDER BY idx DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    
    db = get_db()
    
    # 데이터 가져오기
    board_items = db.execute(base_query, params).fetchall()
    
    # total_items 계산 시 검색 조건에 따라 매개변수 전달
    if search_query:
        total_items = db.execute(count_query, params[:-2]).fetchone()["total"]
    else:
        total_items = db.execute(count_query).fetchone()["total"]
        
    # created_at 값을 datetime 객체로 변환
    board_items = [
        {
            **dict(item),
            "created_at": datetime.fromisoformat(item["created_at"])
        }
        for item in board_items
    ]

    # 총 페이지 수 계산
    total_pages = (total_items + per_page - 1) // per_page

    return render_template(
        "board.html",
        board_items=board_items,
        total_pages=total_pages,
        current_page=page,
        search_query=search_query,
        filter_by=filter_by,
    )

# 게시판 글 상세 조회
@main.route("/board/<int:board_id>", methods=["GET"])
@login_required
def board_detail(board_id):
    # from .models import Board (상단에 기재)
    board_item = Board.query.get_or_404(board_id)  # ID로 게시글 조회, 없으면 404 반환
    
    # 파일 이름 추출
    if board_item.file_path:
        file_name = os.path.basename(board_item.file_path)  # 경로에서 파일 이름만 추출
    else:
        file_name = None
    
    return render_template("board_detail.html", board_item=board_item, file_name=file_name)

# 게시판 글 조회수 증가 - 비동기 처리
@main.route("/board/<int:board_id>/increase_view", methods=["POST"])
@login_required
def increase_view(board_id):
    
    # 원시 SQL로 view_count만 업데이트
    sql = text("UPDATE boardlist SET view_count = view_count + 1 WHERE idx = :board_id")
    db.session.execute(sql, {"board_id": board_id})
    db.session.commit()

    # 최신 view_count 값을 반환
    board_item = Board.query.get(board_id)
    return {"success": True, "view_count": board_item.view_count}, 200



# 게시판 글 등록
@main.route("/board/create", methods=["GET", "POST"])
@login_required
def board_create():
    form = BoardCreateForm()
    if request.method == "POST" and form.validate_on_submit():
        
        title = request.form.get("title")
        content = request.form.get("content")
        file = request.files.get("file")  # 업로드된 파일
        
        if not title or not content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("main.board_create"))

        # 파일 저장 처리
        file_name = None
        if file and file.filename.strip():
            try:
                print("파일 저장 시도 중: ", file.filename)  # 디버깅용 출력
                unique_name = f"{int(time.time())}_{file.filename}"  # 고유한 파일 이름 생성
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name))
                file_name = unique_name
                print("파일 저장 성공: ", file_name)
                
            except Exception as e:
                print("파일 저장 실패: ", str(e))
                flash(f"File upload failed: {str(e)}", "danger")
                return redirect(url_for("main.board_create"))

        # 현재 시간 설정 (KST)
        now = datetime.now(ZoneInfo("Asia/Seoul")).strftime('%Y-%m-%d %H:%M:%S')        
        db = get_db()

        try:
            print("Attempting to execute INSERT with values:")
            print(f"Title: {title}, Content: {content}, User ID: {current_user.user_id}, User Name: {current_user.user_name}, Created At: {now}, Last Updated: {now}, File Path: {file_name}")
            db.execute(
                """
                INSERT INTO boardlist (board_title, board_content, user_id, user_name, created_at, last_updated, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, content, current_user.user_id, current_user.user_name, now, now, file_name)
            )
            
            db.commit()
            flash("Post created successfully!", "success") 
            
            print("--------파일업로드 디버깅 (성공) ----------")
            print("Title:", title)
            print("Content:", content)
            print("File Path:", file_name)
            print("Created At:", now)
            print("Last Updated:", now)
        
            return redirect(url_for("main.board"))  # 게시글 목록 페이지로 이동
        except Exception as e:
            db.rollback()
            
            print("--------파일업로드 디버깅 (실패) ----------")
            print("Title:", title)
            print("Content:", content)
            print("File Path:", file_name)
            print("Created At:", now)
            print("Last Updated:", now)

            print("Database Error: ", str(e))
            flash(f"An error occurred: {e}", "danger")
            
        
    return render_template("board_create.html", form=form)


# 게시글 수정
@main.route("/board/update/<int:board_id>", methods=["GET", "POST"])
@login_required
def board_update(board_id):
    # from .models import Board (상단에 기재)
    board_item = Board.query.get_or_404(board_id)  # 게시글 조회
    
    # 본인이 작성한 글인지 확인
    if board_item.user_id != current_user.user_id:
        flash("You are not authorized to edit this post.", "danger")
        return redirect(url_for("main.board"))

    # 기존 데이터로 폼 초기화
    form = BoardUpdateForm(data={
        "title": board_item.board_title,
        "content": board_item.board_content
    })  
    
    # print("Board Item:", board_item)
    # print("Board Title:", board_item.board_title)
    # print("Board Content:", board_item.board_content)
    
    if request.method == "POST" and form.validate_on_submit():
        # 게시글 수정
        title = request.form.get("title")
        content = request.form.get("content")
        file = request.files.get("file")
        
        # 새 파일 업로드 여부 확인
        if file:
            try:
                ext = os.path.splitext(file.filename)[1]
                unique_name = f"{int(time.time())}_{file.filename}"  # 타임스탬프 + 원래 이름
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name))
                board_item.file_path = unique_name  # 파일 이름만 저장
            except Exception as e:
                flash(f"File upload failed: {str(e)}", "danger")
                return redirect(url_for("main.board_update", board_id=board_id))
        else:
            flash("Keeping the existing file.", "info") # 기존 파일 경로 유지
        
        # 게시글 제목과 내용 업데이트
        board_item.board_title = title
        board_item.board_content = content
        board_item.last_updated = datetime.now(ZoneInfo("Asia/Seoul"))
        
        # 한국 표준시로 현재 시간 저장
        kst = ZoneInfo("Asia/Seoul")
        board_item.last_updated = datetime.now(kst)
        print("최종수정시간 (last_updated) :::::: ", board_item.last_updated)
        print("최종수정시간 datetime.now(kst) :::::: ", datetime.now(kst))
        
        try:
            db.session.commit()
            flash("Post updated successfully!", "success")
            return redirect(url_for("main.board_detail", board_id=board_id))  # 수정 후 상세 페이지로 이동
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
            
    # 기존 파일 이름만 템플릿으로 전달
    file_name = basename(board_item.file_path) if board_item.file_path else None
    return render_template("board_update.html", form=form, board_item=board_item, file_name=file_name)

# 게시판 글 삭제
@main.route("/board/delete/<int:board_id>", methods=["POST"])
@login_required
def board_delete(board_id):
    board_item = Board.query.get_or_404(board_id)

    # 삭제 권한 확인: 작성자이거나 관리자만 가능
    if board_item.user_id != current_user.user_id:
        flash("You are not authorized to delete this post.", "danger")
        return redirect(url_for("main.board"))

    try:
        db.session.delete(board_item)
        db.session.commit()
        flash("Post deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for("main.board"))

# 파일 다운로드 처리
@main.route("/uploads/<file_name>", methods=["GET"])
@login_required
def download_file(file_name):
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        file_name,
        as_attachment=True
    )