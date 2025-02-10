# 애플리케이션 실행 파일입니다.
# Flask 애플리케이션을 시작하는 진입점 역할을 합니다.
# 보통 개발 모드나 프로덕션 모드에서 실행할 수 있도록 설정합니다.


from app import create_app #create_app을 통해 flask 실행시킨다.

app = create_app()

if __name__ == "__main__": 
    app.run(debug=True)

