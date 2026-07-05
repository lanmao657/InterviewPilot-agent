"""add document embedding status fields

Revision ID: 0007_document_embedding_status
Revises: 0006_resize_embedding
Create Date: 2026-07-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0007_document_embedding_status"
down_revision = "0006_resize_embedding"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("documents", "embedding_status"):
        op.add_column(
            "documents",
            sa.Column("embedding_status", sa.String(length=20), nullable=False, server_default="pending"),
        )
    if not _has_column("documents", "embedding_error"):
        op.add_column("documents", sa.Column("embedding_error", sa.Text(), nullable=True))
    if not _has_column("documents", "chunk_count"):
        op.add_column(
            "documents",
            sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    if _has_column("documents", "chunk_count"):
        op.drop_column("documents", "chunk_count")
    if _has_column("documents", "embedding_error"):
        op.drop_column("documents", "embedding_error")
    if _has_column("documents", "embedding_status"):
        op.drop_column("documents", "embedding_status")
