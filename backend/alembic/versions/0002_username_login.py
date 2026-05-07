"""add username login

Revision ID: 0002_username_login
Revises: 0001_initial
Create Date: 2026-05-04
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_username_login"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def _fallback_username(email: str | None, user_id: int) -> str:
    base = (email or "").split("@", 1)[0].strip().casefold()
    if not base or len(base) < 3 or "@" in base:
        base = f"user{user_id}"
    return base[:120]


def _dedupe_username(base: str, user_id: int, seen: set[str]) -> str:
    if base not in seen:
        seen.add(base)
        return base
    suffix = f"-{user_id}"
    username = f"{base[:120 - len(suffix)]}{suffix}"
    seen.add(username)
    return username


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=120), nullable=True))

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, email FROM users ORDER BY id")).mappings()
    seen: set[str] = set()
    for row in rows:
        username = _dedupe_username(_fallback_username(row["email"], row["id"]), row["id"], seen)
        connection.execute(
            sa.text("UPDATE users SET username = :username WHERE id = :id"),
            {"username": username, "id": row["id"]},
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("username", existing_type=sa.String(length=120), nullable=False)
        batch_op.alter_column("email", existing_type=sa.String(length=255), nullable=True)
        batch_op.create_index("ix_users_username", ["username"], unique=True)


def downgrade() -> None:
    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, username, email FROM users ORDER BY id")).mappings()
    for row in rows:
        if row["email"] is None:
            connection.execute(
                sa.text("UPDATE users SET email = :email WHERE id = :id"),
                {"email": f"{row['username']}@example.invalid", "id": row["id"]},
            )

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index("ix_users_username")
        batch_op.alter_column("email", existing_type=sa.String(length=255), nullable=False)
        batch_op.drop_column("username")
