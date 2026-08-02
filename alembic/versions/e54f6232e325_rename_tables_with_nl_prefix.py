"""rename tables with nl prefix

모든 테이블에 서비스 약어 접두사 `nl_`(나의 일기)을 붙인다.

autogenerate를 쓰지 않고 직접 작성한 이유: 이름 변경을 autogenerate에 맡기면
"기존 테이블 삭제 + 새 테이블 생성"으로 인식해 데이터가 전부 사라진다.
rename_table은 데이터를 그대로 둔 채 이름만 바꾼다.

PostgreSQL은 외래키를 이름이 아니라 내부 OID로 참조하므로, 테이블 이름을 바꿔도
FK 제약은 자동으로 새 이름을 따라간다. 따라서 rename 순서는 상관없다.

Revision ID: e54f6232e325
Revises: 187f5272ce29
Create Date: 2026-08-02 22:57:54.525904

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e54f6232e325'
down_revision: Union[str, Sequence[str], None] = '187f5272ce29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (기존 이름, 새 이름) 목록.
TABLE_RENAMES = [
    ("users", "nl_users"),
    ("spaces", "nl_spaces"),
    ("space_members", "nl_space_members"),
    ("schedules", "nl_schedules"),
    ("schedule_participants", "nl_schedule_participants"),
    ("schedule_places", "nl_schedule_places"),
    ("places", "nl_places"),
    ("diary_entries", "nl_diary_entries"),
    ("diary_photos", "nl_diary_photos"),
    ("share_links", "nl_share_links"),
]


def upgrade() -> None:
    """테이블과 시퀀스 이름에 nl_ 접두사를 붙인다."""
    for old_name, new_name in TABLE_RENAMES:
        op.rename_table(old_name, new_name)
        # 테이블 이름을 바꿔도 SERIAL이 쓰는 시퀀스는 옛 이름을 유지하므로 따로 바꿔준다.
        # 동작에는 영향이 없지만 이름이 어긋나면 나중에 읽기 어려워진다.
        op.execute(f"ALTER SEQUENCE IF EXISTS {old_name}_id_seq RENAME TO {new_name}_id_seq")


def downgrade() -> None:
    """접두사를 제거해 원래 이름으로 되돌린다."""
    for old_name, new_name in TABLE_RENAMES:
        op.rename_table(new_name, old_name)
        op.execute(f"ALTER SEQUENCE IF EXISTS {new_name}_id_seq RENAME TO {old_name}_id_seq")
