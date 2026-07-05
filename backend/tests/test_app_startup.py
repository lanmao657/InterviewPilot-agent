from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_application_startup_does_not_create_tables_outside_alembic() -> None:
    main = (PROJECT_ROOT / "app/main.py").read_text(encoding="utf-8")

    assert "create_all" not in main
    assert "Base.metadata" not in main
