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


# 테이블 이름에서 자동 생성된 인덱스/제약조건 이름 목록.
# rename_table은 테이블만 바꾸고 이에 딸린 인덱스 이름은 그대로 두기 때문에 따로 처리한다.
#
# ix_schedules_space_id는 반드시 바꿔야 한다. 모델의 index=True가 새 테이블명 기준으로
# ix_nl_schedules_space_id를 기대하므로, 두지 않으면 alembic check가 계속 불일치를 보고한다.
# 나머지 _pkey/_key는 PostgreSQL이 자동 생성한 이름이라 동작에는 영향이 없지만,
# DBeaver에서 볼 때 테이블명과 어긋나지 않도록 함께 맞춘다.
#
# 주의: 모델에 직접 이름을 준 제약조건(uq_diary_schedule, ck_spaces_type 등)은 건드리지 않는다.
#       SQLAlchemy가 그 이름 그대로를 기대하므로 바꾸면 오히려 불일치가 생긴다.
INDEX_RENAMES = [
    ("ix_schedules_space_id", "ix_nl_schedules_space_id"),
    ("users_pkey", "nl_users_pkey"),
    ("users_email_key", "nl_users_email_key"),
    ("users_nickname_key", "nl_users_nickname_key"),
    ("spaces_pkey", "nl_spaces_pkey"),
    ("spaces_uuid_key", "nl_spaces_uuid_key"),
    ("spaces_join_code_key", "nl_spaces_join_code_key"),
    ("space_members_pkey", "nl_space_members_pkey"),
    ("schedules_pkey", "nl_schedules_pkey"),
    ("schedule_participants_pkey", "nl_schedule_participants_pkey"),
    ("schedule_places_pkey", "nl_schedule_places_pkey"),
    ("places_pkey", "nl_places_pkey"),
    ("diary_entries_pkey", "nl_diary_entries_pkey"),
    ("diary_photos_pkey", "nl_diary_photos_pkey"),
    ("share_links_pkey", "nl_share_links_pkey"),
    ("share_links_token_key", "nl_share_links_token_key"),
]


def upgrade() -> None:
    """테이블·시퀀스·인덱스 이름에 nl_ 접두사를 붙인다."""
    for old_name, new_name in TABLE_RENAMES:
        op.rename_table(old_name, new_name)
        # 테이블 이름을 바꿔도 SERIAL이 쓰는 시퀀스는 옛 이름을 유지하므로 따로 바꿔준다.
        op.execute(f"ALTER SEQUENCE IF EXISTS {old_name}_id_seq RENAME TO {new_name}_id_seq")

    for old_name, new_name in INDEX_RENAMES:
        # 제약조건을 뒷받침하는 인덱스도 ALTER INDEX로 이름을 바꾸면 제약조건 이름까지 함께 바뀐다.
        op.execute(f"ALTER INDEX IF EXISTS {old_name} RENAME TO {new_name}")


def downgrade() -> None:
    """접두사를 제거해 원래 이름으로 되돌린다."""
    for old_name, new_name in INDEX_RENAMES:
        op.execute(f"ALTER INDEX IF EXISTS {new_name} RENAME TO {old_name}")

    for old_name, new_name in TABLE_RENAMES:
        op.rename_table(new_name, old_name)
        op.execute(f"ALTER SEQUENCE IF EXISTS {new_name}_id_seq RENAME TO {old_name}_id_seq")
