# 나의 일기(내일)

`나의 일기(내일)`은 앞으로 할 일을 정하고, 지나간 하루를 사진과 글로 남기는 장소 기반 일기 및 일정 앱입니다.

이 저장소는 FastAPI 백엔드와 React(Vite) 프론트엔드로 구성되어 있습니다.

## 문서

- [제품 기획서](./docs/PRODUCT_SPEC.md)
- [개발 인수인계 문서](./docs/DEVELOPMENT_BRIEF.md)
- [AI 도구 이해 노트](./docs/AI_WORKFLOW_NOTES.md)

다른 개발자는 위 문서 두 개를 먼저 읽고 MVP 범위, 데이터 모델, API, 화면 구조를 확인하면 됩니다.

## 프로젝트 구조

```text
app/        FastAPI backend
tests/      Backend tests
frontend/   React frontend
docs/       Product and development documents
```

## 백엔드 실행

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/v1/health`

## 백엔드 테스트

```powershell
pytest -q
```

## 프론트엔드 실행

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

PowerShell 실행 정책 때문에 `npm`이 막히면 `npm.cmd`를 사용하세요.

## 프론트엔드 빌드

```powershell
cd frontend
npm.cmd run build
```

## Docker 실행

```powershell
docker compose up --build
```
