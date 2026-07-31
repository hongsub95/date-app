"""API 오류 응답 형식을 한 곳에서 통일하는 모듈.

FastAPI 기본 오류는 `{"detail": "..."}` 형태라 오류 종류를 코드로 구분할 수 없고,
어떤 입력 필드가 문제인지도 알 수 없다. 프론트엔드가 오류를 화면에 매핑하려면
기계가 읽을 수 있는 코드와 필드명이 필요하므로 모든 오류를 아래 형태로 통일한다.

    {
      "code": "INVALID_JOIN_CODE",
      "message": "참여 번호를 확인해 주세요.",
      "field": "join_code"
    }

- code: 프론트엔드가 분기 처리에 쓰는 불변 식별자. 문구가 바뀌어도 code는 유지한다.
- message: 사용자에게 그대로 보여줄 수 있는 한국어 문구.
- field: 입력값 문제일 때 어떤 필드인지. 해당 없으면 null.
"""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """API가 의도적으로 발생시키는 오류의 베이스.

    서비스 계층에서 이 예외를 던지면 아래 핸들러가 통일된 JSON으로 변환한다.

    :param code: 프론트엔드가 분기에 사용할 식별자 (예: EMAIL_ALREADY_EXISTS)
    :param message: 사용자에게 보여줄 한국어 문구
    :param status_code: HTTP 상태 코드
    :param field: 문제가 된 요청 필드명. 특정 필드와 무관하면 None
    """

    def __init__(self, code: str, message: str, status_code: int, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field


def _error_body(code: str, message: str, field: str | None = None) -> dict[str, str | None]:
    """오류 응답 본문을 만든다. field는 항상 키로 존재하되 값이 없으면 null이다.

    키를 조건부로 빼면 프론트엔드가 매번 존재 여부를 확인해야 하므로 항상 포함시킨다.
    """
    return {"code": code, "message": message, "field": field}


def register_error_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 오류 핸들러를 등록한다. main.py에서 앱 생성 직후 한 번 호출한다."""

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        """서비스 계층이 의도적으로 던진 오류를 통일된 형식으로 변환한다."""
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.field),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        """Pydantic 검증 실패(422)를 통일된 형식으로 변환한다.

        Pydantic은 여러 필드의 오류를 한꺼번에 돌려주지만, 화면에서는 보통 첫 번째
        오류부터 고치게 되므로 대표 오류 하나를 최상위에 올리고 전체 목록은
        details에 함께 담는다.
        """
        errors = exc.errors()
        first = errors[0] if errors else {}

        # loc은 ("body", "password")처럼 위치 경로다. 앞의 body/query 같은 출처를 빼고
        # 실제 필드명만 프론트엔드에 넘긴다.
        location = [str(part) for part in first.get("loc", []) if part not in ("body", "query", "path")]
        field = location[-1] if location else None

        body = _error_body(
            code="VALIDATION_ERROR",
            message=first.get("msg", "입력값을 확인해 주세요."),
            field=field,
        )
        body["details"] = [
            {
                "field": ".".join(
                    str(part) for part in err.get("loc", []) if part not in ("body", "query", "path")
                )
                or None,
                "message": err.get("msg", ""),
            }
            for err in errors
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(body),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        """FastAPI 내부에서 발생하는 HTTPException(404, 405 등)도 같은 형식으로 맞춘다.

        이렇게 해두면 프론트엔드는 "모든 오류 응답은 code/message/field를 가진다"는
        단 하나의 규칙만 알면 된다.
        """
        code = _HTTP_STATUS_TO_CODE.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(code, str(exc.detail), None),
            headers=getattr(exc, "headers", None),
        )


# 프레임워크가 자동으로 내는 오류에 붙일 코드. 여기 없는 상태 코드는 HTTP_ERROR가 된다.
_HTTP_STATUS_TO_CODE = {
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    status.HTTP_409_CONFLICT: "CONFLICT",
    status.HTTP_429_TOO_MANY_REQUESTS: "TOO_MANY_REQUESTS",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_ERROR",
}
