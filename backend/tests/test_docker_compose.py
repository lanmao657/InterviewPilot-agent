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


def test_production_nginx_disables_api_proxy_buffering() -> None:
    nginx = (PROJECT_ROOT / "frontend/nginx.conf").read_text(encoding="utf-8")
    api_location = nginx.split("location /api", maxsplit=1)[1].split("}", maxsplit=1)[0]

    assert "proxy_buffering off;" in api_location
