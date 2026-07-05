from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_dev_compose_does_not_install_dependencies_on_every_start() -> None:
    compose = (PROJECT_ROOT / "docker-compose.override.yml").read_text(encoding="utf-8")

    assert "pip install" not in compose
    assert "npm install" not in compose
    assert "npm ci" not in compose


def test_dev_compose_keeps_frontend_dependencies_inside_container_volume() -> None:
    compose = (PROJECT_ROOT / "docker-compose.override.yml").read_text(encoding="utf-8")

    assert "frontend-node-modules:" in compose
    assert "node_modules" in compose
