from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_docker_smoke_script_checks_postgres_migrations_and_health() -> None:
    script = (PROJECT_ROOT / "scripts/docker-smoke.ps1").read_text(encoding="utf-8")

    assert "docker compose ps" in script
    assert "pg_isready" in script
    assert "alembic current" in script
    assert "http://localhost:8000/health" in script
