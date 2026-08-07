"""add user role and seed master account

Revision ID: b3c32666bfc6
Revises: 32aa082cae06
Create Date: 2026-08-08

권한 등급(nl_users.role)을 추가하고, 운영자가 쓸 마스터 계정 하나를 함께 넣는다.

메뉴의 required_role도 같이 정수로 바꾼다. 문자열('admin')로 두면 int인 users.role과
영원히 같아지지 않아 관리자 메뉴가 아무에게도 보이지 않기 때문이다. 현재 nl_menus의
required_role은 전부 NULL이라 값 손실 없이 타입만 바꿀 수 있다.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c32666bfc6'
down_revision: Union[str, Sequence[str], None] = '32aa082cae06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 마스터 계정 정보. app/users/models.py의 USER_ROLE_MASTER와 같은 값이다.
MASTER_EMAIL = "hong9506@gmail.com"
MASTER_NICKNAME = "홍섭"
MASTER_ROLE = 0

# 평문 "test"의 bcrypt 해시(cost 12). bcrypt는 salt를 해시 문자열 안에 담기 때문에
# 이 값 하나로 어느 환경에서든 "test"가 통과한다.
#
# 해시를 마이그레이션에 박아 넣은 이유: 여기서 bcrypt.hashpw()를 호출하면 환경마다
# 다른 해시가 생겨 "DB마다 값이 다른" 마이그레이션이 된다. 마이그레이션은 어디서
# 돌려도 같은 결과가 나와야 하므로 미리 계산한 값을 고정한다.
MASTER_PASSWORD_HASH = "$2b$12$YoBKY0MjfJeJM1VmaM57/eHDLtRMZ1t2Fq5suUvjN/Dkoom3UzFiy"

# 회원가입과 동일하게 개인 스페이스를 함께 만들어 준다 (app/auth/service.py register_user).
PERSONAL_SPACE_NAME = "나의 일정"


def upgrade() -> None:
    """Upgrade schema."""
    # 기존 행은 전부 일반 회원(1)으로 채운다. server_default를 주지 않으면
    # NOT NULL 컬럼을 추가할 수 없다.
    op.add_column(
        "nl_users",
        sa.Column("role", sa.Integer(), server_default="1", nullable=False),
    )

    # 문자열 -> 정수 변환. 값이 전부 NULL이라 USING 절 없이도 되지만, 혹시 값이
    # 들어 있는 환경에서도 실패하지 않도록 명시적으로 캐스팅한다.
    op.alter_column(
        "nl_menus",
        "required_role",
        existing_type=sa.String(length=20),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="NULLIF(required_role, '')::integer",
    )

    _seed_master_account()


def _seed_master_account() -> None:
    """마스터 계정과 그 개인 스페이스를 만든다.

    회원가입 API를 타지 않고 직접 넣기 때문에, register_user()가 하는 세 가지를
    여기서 똑같이 해줘야 반쪽짜리 계정이 되지 않는다.

    1. 개인 스페이스 생성
    2. 본인을 owner 멤버로 등록 (권한 검사는 SpaceMember를 보므로 필수)
    3. default_space_id 설정 (앱이 이 값으로 첫 화면을 연다)

    :raises RuntimeError: 다른 계정이 마스터 닉네임을 이미 쓰고 있어 만들 수 없을 때
    """
    connection = op.get_bind()

    # 개발 중 API로 먼저 가입해 둔 환경을 고려한다. 이미 있으면 새로 만들지 않고
    # 등급만 마스터로 올린다. 여기서 그냥 건너뛰면 "마이그레이션은 성공했는데
    # 마스터 권한은 없는" 상태가 조용히 남는다. 비밀번호와 닉네임은 건드리지 않는다.
    existing_id = connection.execute(
        sa.text("SELECT id FROM nl_users WHERE email = :email"), {"email": MASTER_EMAIL}
    ).scalar()
    if existing_id is not None:
        connection.execute(
            sa.text("UPDATE nl_users SET role = :role WHERE id = :id"),
            {"role": MASTER_ROLE, "id": existing_id},
        )
        return

    # 닉네임은 UNIQUE라, 다른 사람이 선점했다면 INSERT가 실패한다. 알 수 없는
    # 제약 위반으로 죽는 대신 무엇을 해야 하는지 알려주고 멈춘다.
    nickname_owner = connection.execute(
        sa.text("SELECT email FROM nl_users WHERE nickname = :nickname"),
        {"nickname": MASTER_NICKNAME},
    ).scalar()
    if nickname_owner is not None:
        raise RuntimeError(
            f"닉네임 '{MASTER_NICKNAME}'을(를) 다른 계정({nickname_owner})이 쓰고 있어 "
            f"마스터 계정을 만들 수 없습니다. 그 계정의 닉네임을 바꾸거나 이 마이그레이션의 "
            f"MASTER_NICKNAME을 수정하세요."
        )

    user_id = connection.execute(
        sa.text(
            """
            INSERT INTO nl_users (email, password_hash, nickname, role)
            VALUES (:email, :password_hash, :nickname, :role)
            RETURNING id
            """
        ),
        {
            "email": MASTER_EMAIL,
            "password_hash": MASTER_PASSWORD_HASH,
            "nickname": MASTER_NICKNAME,
            "role": MASTER_ROLE,
        },
    ).scalar_one()

    # 개인 스페이스는 join_code가 NULL이어야 한다 (ck_spaces_personal_has_no_join_code).
    space_id = connection.execute(
        sa.text(
            """
            INSERT INTO nl_spaces (type, name, owner_id)
            VALUES ('personal', :name, :owner_id)
            RETURNING id
            """
        ),
        {"name": PERSONAL_SPACE_NAME, "owner_id": user_id},
    ).scalar_one()

    connection.execute(
        sa.text(
            """
            INSERT INTO nl_space_members (space_id, user_id, role, status)
            VALUES (:space_id, :user_id, 'owner', 'active')
            """
        ),
        {"space_id": space_id, "user_id": user_id},
    )

    connection.execute(
        sa.text("UPDATE nl_users SET default_space_id = :space_id WHERE id = :user_id"),
        {"space_id": space_id, "user_id": user_id},
    )


def downgrade() -> None:
    """Downgrade schema.

    마스터 계정은 **일부러 지우지 않는다.** upgrade가 새로 만들었는지, 원래 있던
    계정을 승격만 했는지 여기서는 구분할 수 없다. nl_spaces.owner_id가 CASCADE라
    잘못 지우면 그 사람의 스페이스와 일정·일기까지 함께 사라진다. 되돌릴 수 없는
    손실을 감수하느니 계정 한 개가 남는 편이 낫다. 계정이 필요 없다면 직접 지운다.
    """
    op.alter_column(
        "nl_menus",
        "required_role",
        existing_type=sa.Integer(),
        type_=sa.String(length=20),
        existing_nullable=True,
        postgresql_using="required_role::text",
    )
    op.drop_column("nl_users", "role")
