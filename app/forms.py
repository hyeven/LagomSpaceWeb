# Flask-WTF를 사용해 폼을 정의합니다.
# 예: 로그인, 회원가입, 게시글 작성 폼.
# flask-wtf 는 폼을 Python 클래스 형태로 정의하고, 입력 검증 및 CSRF 보호를 제공


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class SignUpForm(FlaskForm):
    user_id = StringField("User ID", validators=[DataRequired(), Length(min=4, max=50)])
    user_name = StringField("Username", validators=[DataRequired(), Length(min=4, max=20)])
    user_email = StringField("Email", validators=[DataRequired(message="이메일은 필수 입력 항목입니다."), Email(message="유효한 이메일 주소를 입력하세요.")])
    user_passwd = PasswordField("Password", validators=[DataRequired(message="비밀번호는 필수 입력 항목입니다."), Length(min=6, message="비밀번호는 최소 6자 이상이어야 합니다.")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("user_passwd")])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    user_id = StringField("User ID", validators=[DataRequired()])
    user_passwd = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
    
    
class MyPageForm(FlaskForm):
    user_id = StringField("User ID", validators=[DataRequired(), Length(min=4, max=50)])
    user_name = StringField("Username", validators=[DataRequired(), Length(min=4, max=20)])
    user_email = StringField("Email", validators=[DataRequired(), Email()])
    user_passwd = PasswordField('Password', validators=[Optional(), Length(min=6, message="Password must be at least 6 characters.")])
    submit = SubmitField("Update")
    
    
class BoardCreateForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Title is required."),
            Length(max=255, message="Title cannot exceed 255 characters.")
        ]
    )
    content = TextAreaField(
        "Content",
        validators=[DataRequired(message="Content is required.")]
    )
    submit = SubmitField("Create Post") 
    
    
class BoardUpdateForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Title is required."),
            Length(max=255, message="Title cannot exceed 255 characters.")
        ]
    )
    content = TextAreaField(
        "Content",
        validators=[DataRequired(message="Content is required.")]
    )
    submit = SubmitField("Save Changes")
