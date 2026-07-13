Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root

try {
    docker compose ps

    $backendContainer = docker compose ps -q backend
    if (-not $backendContainer) {
        throw "backend service is not running. Start the stack with: docker compose up -d"
    }

    $dbUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "interviewpilot" }
    $dbName = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "interviewpilot" }

    docker compose exec -T db pg_isready -U $dbUser -d $dbName
    docker compose exec -T backend alembic current

    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    if ($health.status -ne "ok") {
        throw "backend health check returned unexpected status: $($health | ConvertTo-Json -Compress)"
    }

    Write-Host "Docker smoke check passed."
}
finally {
    Pop-Location
}
