# 나의 일기(내일)

`나의 일기(내일)`은 앞으로 할 일을 정하고, 지나간 하루를 사진과 글로 남기는 장소 기반 일기 및 일정 앱입니다.

이 저장소는 FastAPI 백엔드와 React(Vite) 프론트엔드로 구성되어 있습니다.

## 문서

- [제품 기획서](./docs/PRODUCT_SPEC.md)
- [개발 인수인계 문서](./docs/DEVELOPMENT_BRIEF.md)
- [스페이스 모델 명세](./docs/SPACE_MODEL_SPEC.md)
- [화면 디자인 명세](./docs/DESIGN_SPEC.md)
- **[API 명세 (프론트엔드 연동용)](./docs/API_SPEC.md)**
- [AI 도구 이해 노트](./docs/AI_WORKFLOW_NOTES.md)

백엔드 개발자는 기획서와 인수인계 문서를 먼저 읽고, **프론트엔드 개발자는 [API 명세](./docs/API_SPEC.md)부터 읽으면 됩니다.**

## 프로젝트 구조

```text
app/        FastAPI backend
tests/      Backend tests
frontend/   React frontend
docs/       Product and development documents
```

## 백엔드 실행

PostgreSQL이 먼저 떠 있어야 합니다. 아래 과정을 한 번에 실행하려면 `.\dev.ps1`을 쓰세요.

```powershell
# 1) DB 컨테이너 실행 (PostgreSQL + pgAdmin)
docker compose up -d db pgadmin

# 2) 가상환경 준비
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3) .env 준비 (.env.example을 복사한 뒤 값을 채웁니다)
copy .env.example .env

# 4) DB 스키마 반영
alembic upgrade head

# 5) 서버 실행
uvicorn app.main:app --reload
```

| 용도 | 주소 |
|---|---|
| API | `http://127.0.0.1:8000` |
| Swagger UI (호출 테스트) | `http://127.0.0.1:8000/docs` |
| ReDoc (읽기용 문서) | `http://127.0.0.1:8000/redoc` |
| OpenAPI JSON (클라이언트 생성용) | `http://127.0.0.1:8000/openapi.json` |
| Health check | `http://127.0.0.1:8000/api/v1/health` |
| pgAdmin | `http://127.0.0.1:5050` |

## 백엔드 테스트

테스트는 개발용 DB(`nailgi`)가 아니라 별도의 `nailgi_test` DB를 자동으로 만들어 사용합니다.
DB 컨테이너가 실행 중이어야 합니다.

```powershell
pytest -q
```

## DB 마이그레이션

모델을 수정한 뒤에는 마이그레이션을 만들어 적용합니다.

```powershell
# 모델 변경사항 감지해서 마이그레이션 파일 생성
alembic revision --autogenerate -m "변경 내용 설명"

# 적용
alembic upgrade head

# 되돌리기 (한 단계)
alembic downgrade -1
```

새 모델을 추가하면 `app/models.py`에도 등록해야 마이그레이션에 잡힙니다.

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
