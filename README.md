# FastAPI Setup

## 1) Python 설치
이 환경에서는 아직 Python이 설치되어 있지 않습니다. 먼저 Python 3.11+를 설치하세요.

## 2) 환경변수 파일 준비
```powershell
Copy-Item .env.example .env
```

## 3) 가상환경 및 의존성 설치
PowerShell에서 `date-app`로 이동 후:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4) 서버 실행
```powershell
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/v1/health`

## 5) 테스트 실행
```powershell
pytest -q
```

## Docker 실행
```powershell
docker compose up --build
```
