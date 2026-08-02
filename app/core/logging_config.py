"""애플리케이션 로깅 설정.

uvicorn이 자체 로거를 쓰기 때문에, 아무 설정도 하지 않으면 우리 코드에서 남긴 로그는
형식이 제각각이거나 아예 보이지 않는다. 여기서 형식과 레벨을 한 번에 맞춘다.

로그는 파일이 아니라 표준 출력(stdout)으로 내보낸다. 나중에 서버에 올렸을 때
Docker나 systemd가 표준 출력을 수집해 주므로, 애플리케이션이 파일 경로와 로테이션을
직접 관리하지 않는 편이 단순하고 사고가 적다.
"""

import logging
import sys

from app.core.config import get_settings

settings = get_settings()

# 시각 · 레벨 · 로거이름 · 메시지 순서. 로거 이름이 있어야 어느 모듈이 남긴 로그인지 구분된다.
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """앱 전체 로깅을 초기화한다. main.py에서 앱 생성 시 한 번만 호출한다."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT))

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())

    # 서버가 --reload로 여러 번 초기화될 때 핸들러가 중복 등록되면 같은 로그가
    # 두 번, 세 번 찍힌다. 기존 핸들러를 비우고 새로 단다.
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # uvicorn은 자기 로거에 핸들러를 따로 달아둔다. 그대로 두면 요청 로그만
    # 다른 형식으로 나오므로, 핸들러를 떼고 위에서 만든 루트 핸들러를 타게 한다.
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    # SQLAlchemy가 실행하는 SQL 전문을 볼지 결정한다.
    # 켜면 모든 쿼리가 찍혀 디버깅에 좋지만 로그가 매우 길어지므로 기본은 꺼둔다.
    sql_level = logging.INFO if settings.db_echo else logging.WARNING
    logging.getLogger("sqlalchemy.engine").setLevel(sql_level)
