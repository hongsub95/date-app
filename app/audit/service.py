"""감사 로그 기록 서비스.

라우터나 서비스에서 `record()` 한 줄만 호출하면 되도록 감싼다.

설계 원칙: **감사 로그 기록이 실패해도 본래 작업은 성공해야 한다.**
로그를 남기지 못했다고 로그인이 실패하면 사용자에게 더 큰 피해다. 대신 실패를
조용히 넘기지 않고 애플리케이션 로그로 남겨 문제를 알아챌 수 있게 한다.
"""

import ipaddress
import logging

from fastapi import Request
from sqlalchemy.orm import Session

from app.audit.models import AuditLog

logger = logging.getLogger("app.audit")

# user_agent 컬럼 길이. 초과분은 잘라서 저장한다.
MAX_USER_AGENT_LENGTH = 500


def _normalize_ip(raw: str | None) -> str | None:
    """IP 문자열이 실제 IP 형식일 때만 돌려주고, 아니면 None을 반환한다.

    ip_address 컬럼이 PostgreSQL의 INET 타입이라 형식에 맞지 않는 값을 넣으면
    INSERT가 실패한다. 그런데 이 값의 출처인 X-Forwarded-For 헤더는 클라이언트가
    마음대로 채울 수 있다. 검증하지 않으면 아무 문자열이나 넣어 감사 로그 기록을
    깨뜨릴 수 있고, 회원가입처럼 같은 트랜잭션에 묶인 작업까지 실패한다.
    """
    if not raw:
        return None
    try:
        return str(ipaddress.ip_address(raw))
    except ValueError:
        # 위조된 헤더이거나 테스트 클라이언트의 가짜 호스트명 등. IP 없이 기록한다.
        return None


def extract_client_info(request: Request | None) -> tuple[str | None, str | None]:
    """요청에서 접속 IP와 User-Agent를 뽑는다.

    :param request: FastAPI 요청 객체. 없으면 (None, None)
    :return: (ip_address, user_agent). IP 형식이 아니면 ip_address는 None
    """
    if request is None:
        return None, None

    # 리버스 프록시(nginx 등) 뒤에 있으면 request.client.host는 프록시 IP가 된다.
    # X-Forwarded-For의 첫 번째 값이 실제 클라이언트 IP다.
    #
    # 주의: 이 헤더는 클라이언트가 위조할 수 있다. 신뢰하려면 프록시가 헤더를 덮어쓰도록
    # 설정해야 한다. 실서버 배포 시 프록시 설정을 함께 점검해야 한다.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip_address = _normalize_ip(forwarded.split(",")[0].strip())
    else:
        ip_address = _normalize_ip(request.client.host if request.client else None)

    user_agent = request.headers.get("user-agent")
    if user_agent:
        # 비정상적으로 긴 User-Agent를 보내 INSERT를 깨뜨리는 것도 막는다.
        user_agent = user_agent[:MAX_USER_AGENT_LENGTH]

    return ip_address, user_agent


def record(
    db: Session,
    action: str,
    *,
    user_id: int | None = None,
    actor_email: str | None = None,
    resource_type: str | None = None,
    resource_id: int | None = None,
    request: Request | None = None,
    detail: dict | None = None,
    commit: bool = True,
) -> None:
    """감사 로그를 한 줄 남긴다.

    :param db: DB 세션
    :param action: AuditAction 상수 중 하나
    :param user_id: 행위자 id. 로그인 실패처럼 특정할 수 없으면 None
    :param actor_email: 행위 시점의 이메일 스냅샷. 실패 시에는 시도한 이메일
    :param resource_type: 대상 종류 (예: "space"). 대상이 없으면 None
    :param resource_id: 대상 id
    :param request: 접속 IP·User-Agent를 뽑을 요청 객체
    :param detail: 행위별 추가 정보 (실패 사유, 변경 내용 등)
    :param commit: False면 호출한 쪽의 트랜잭션에 합류한다. 회원가입처럼 본래 작업과
        하나의 트랜잭션으로 묶어야 할 때 사용한다.
    """
    ip_address, user_agent = extract_client_info(request)

    entry = AuditLog(
        user_id=user_id,
        actor_email=actor_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        detail=detail,
    )

    try:
        db.add(entry)
        if commit:
            db.commit()
    except Exception as exc:
        # 감사 로그 실패가 본래 작업을 막아서는 안 된다. 다만 조용히 넘기면
        # 이력이 비어가는 것을 아무도 모르게 되므로 반드시 로그로 알린다.
        logger.error("감사 로그 기록 실패 | action=%s user_id=%s | %s", action, user_id, exc)
        if commit:
            db.rollback()
