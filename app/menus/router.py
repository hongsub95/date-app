"""메뉴 엔드포인트.

메뉴를 DB에서 내려주기 때문에, 이름·순서·노출 여부를 바꿔도 프론트엔드를 다시
배포할 필요가 없다.
"""

from typing import Annotated

from fastapi import APIRouter, Query

from app.auth.dependencies import CurrentUser, DbSession
from app.menus import service
from app.menus.models import MENU_SCOPE_ADMIN, MENU_SCOPE_APP
from app.menus.schemas import MenuListResponse

router = APIRouter(prefix="/menus", tags=["menus"])


@router.get(
    "",
    response_model=MenuListResponse,
    summary="메뉴 목록 조회",
    description=(
        "화면에 표시할 메뉴를 트리 형태로 돌려준다. "
        "`scope=app`은 앱 하단 탭, `scope=admin`은 관리자 메뉴다. "
        "비활성 메뉴와 권한이 없는 메뉴는 응답에 포함되지 않으므로, "
        "프론트엔드는 받은 목록을 그대로 그리면 된다."
    ),
)
def list_menus(
    current_user: CurrentUser,
    db: DbSession,
    scope: Annotated[str, Query(pattern=f"^({MENU_SCOPE_APP}|{MENU_SCOPE_ADMIN})$")] = MENU_SCOPE_APP,
) -> MenuListResponse:
    """메뉴 목록 조회. 로그인한 사용자만 호출할 수 있다."""
    return MenuListResponse(menus=service.get_menu_tree(db, scope=scope, role=current_user.role))
