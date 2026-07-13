from pathlib import Path


def test_resize_embedding_migration_does_not_null_not_nullable_column() -> None:
    migration = Path("alembic/versions/0006_resize_embedding.py").read_text(encoding="utf-8")

    assert "UPDATE document_chunks SET embedding = NULL" not in migration
    assert "DELETE FROM document_chunks" in migration


def test_document_embedding_status_migration_adds_status_fields() -> None:
    migration = Path("alembic/versions/0007_document_embedding_status.py").read_text(encoding="utf-8")

    assert "embedding_status" in migration
    assert "embedding_error" in migration
    assert "chunk_count" in migration
    assert 'server_default="pending"' in migration


def test_document_embedding_status_migration_is_idempotent_for_existing_columns() -> None:
    migration = Path("alembic/versions/0007_document_embedding_status.py").read_text(encoding="utf-8")

    assert "inspect(op.get_bind())" in migration
    assert "_has_column" in migration
    assert 'if not _has_column("documents", "embedding_status")' in migration
