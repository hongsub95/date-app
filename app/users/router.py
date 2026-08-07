"""사용자 설정 엔드포인트.

인증(로그인·회원가입)은 app/auth가 담당하고, 여기서는 로그인한 사용자가 자기
설정을 바꾸는 API를 다룬다.
"""

from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, DbSession
from app.spaces import service as space_service
from app.spaces.schemas import DefaultSpaceUpdateRequest, SpaceResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.put(
    "/me/default-space",
    response_model=SpaceResponse,
    summary="기본 스페이스 변경",
    description=(
        "앱 실행 시 열리는 스페이스를 바꾼다. 자기가 활성 멤버인 스페이스만 지정할 수 있다. "
        "여기서 지정한 스페이스는 지정을 바꾸기 전까지 삭제할 수 없다."
    ),
)
def update_default_space(
    payload: DefaultSpaceUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> SpaceResponse:
    """기본 스페이스 변경."""
    return space_service.set_default_space(db, current_user, payload.space_id)
