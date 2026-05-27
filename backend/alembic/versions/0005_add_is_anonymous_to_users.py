"""add is_anonymous to users

Revision ID: 0005_add_is_anonymous_to_users
Revises: 0004_add_document_chunks
Create Date: 2026-05-27
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_add_is_anonymous_to_users"
down_revision = "0004_add_document_chunks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 为 users 表添加 is_anonymous 字段，用于标识匿名用户
    op.add_column(
        "users",
        sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    # 移除 users 表的 is_anonymous 字段
    op.drop_column("users", "is_anonymous")
