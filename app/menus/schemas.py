"""메뉴 API의 응답 형태."""

from pydantic import BaseModel, ConfigDict


class MenuResponse(BaseModel):
    """메뉴 항목 하나. 하위 메뉴가 있으면 children에 중첩된다.

    프론트엔드가 그대로 순회해 렌더링할 수 있도록 트리 형태로 내려준다.
    평면 배열로 주면 클라이언트가 매번 부모-자식을 조립해야 한다.
    """

    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    icon: str | None
    path: str | None
    # 하위 메뉴가 없으면 빈 배열. null이 아니라 []로 주어야 클라이언트가
    # 존재 여부를 확인하지 않고 바로 순회할 수 있다.
    children: list["MenuResponse"] = []


class MenuListResponse(BaseModel):
    """메뉴 목록 응답."""

    menus: list[MenuResponse]
