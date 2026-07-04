from pathlib import Path


def test_resize_embedding_migration_does_not_null_not_nullable_column() -> None:
    migration = Path("alembic/versions/0006_resize_embedding.py").read_text(encoding="utf-8")

    assert "UPDATE document_chunks SET embedding = NULL" not in migration
    assert "DELETE FROM document_chunks" in migration
