"""resize embedding vector from 1536 to 1024

Revision ID: 0006_resize_embedding
Revises: 0005_add_is_anonymous_to_users
Create Date: 2026-05-30
"""

from alembic import op

revision = "0006_resize_embedding"
down_revision = "0005_add_is_anonymous_to_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgvector 支持直接 ALTER TYPE 修改向量维度
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1024)")
    # 删除旧的索引（如果有维度相关的索引需要重建）
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding")
    # 清空旧的 1536 维向量数据，需要重新生成 embedding
    op.execute("UPDATE document_chunks SET embedding = NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536)")
    op.execute("UPDATE document_chunks SET embedding = NULL")
