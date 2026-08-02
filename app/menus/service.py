"""메뉴 조회 로직."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.menus.models import MENU_SCOPE_APP, Menu
from app.menus.schemas import MenuResponse


def get_menu_tree(db: Session, scope: str = MENU_SCOPE_APP, role: str | None = None) -> list[MenuResponse]:
    """지정한 영역의 활성 메뉴를 트리 형태로 돌려준다.

    :param db: DB 세션
    :param scope: "app"(앱 하단 탭) 또는 "admin"(관리자 메뉴)
    :param role: 요청자의 권한. required_role이 걸린 메뉴는 권한이 맞을 때만 포함한다.
        None이면 권한 제한이 없는 메뉴만 나온다.
    :return: 최상위 메뉴 목록. 하위 메뉴는 각 항목의 children에 들어간다.
    """
    # 전체를 한 번에 읽고 메모리에서 트리를 만든다. 계층을 따라 재귀 질의를 하면
    # 깊이만큼 왕복이 늘어나는데, 메뉴는 많아야 수십 건이라 한 번에 읽는 편이 빠르다.
    rows = db.scalars(
        select(Menu)
        .where(Menu.scope == scope, Menu.is_active.is_(True))
        .order_by(Menu.sort_order, Menu.id)
    ).all()

    visible = [row for row in rows if _is_visible(row, role)]

    # code를 키로 노드를 만들어 두고, 부모를 찾아 children에 매단다.
    nodes: dict[int, MenuResponse] = {
        row.id: MenuResponse(code=row.code, name=row.name, icon=row.icon, path=row.path, children=[])
        for row in visible
    }

    roots: list[MenuResponse] = []
    for row in visible:
        node = nodes[row.id]
        parent = nodes.get(row.parent_id) if row.parent_id else None
        if parent is None:
            # 부모가 없거나, 부모가 권한 때문에 걸러진 경우다. 후자라면 자식만 남아
            # 붕 뜨게 되므로 최상위로 올리지 않고 함께 감춘다.
            if row.parent_id is None:
                roots.append(node)
        else:
            parent.children.append(node)

    return roots


def _is_visible(menu: Menu, role: str | None) -> bool:
    """요청자의 권한으로 이 메뉴를 볼 수 있는지 판단한다.

    required_role이 없으면 누구나 볼 수 있고, 있으면 권한이 정확히 일치해야 한다.
    등급 간 포함 관계(예: super_admin이 admin 메뉴도 봄)는 users.role 컬럼과
    권한 체계가 확정된 뒤에 정한다.
    """
    if menu.required_role is None:
        return True
    return role == menu.required_role
