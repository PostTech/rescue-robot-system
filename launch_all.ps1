# Refresh environment path
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Output "=== Starting E2E System Ingestion ==="

# 1. Run docker-compose
Write-Output "Booting up Docker Containers (Postgres/MinIO)..."
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to boot Docker compose. Please ensure Docker Desktop is running!"
    exit 1
}

# Wait a moment for Postgres to boot
Write-Output "Waiting 4 seconds for database initialization..."
Start-Sleep -Seconds 4

# 2. Start Go Core Server
Write-Output "Starting Go Core Backend..."
cd go_core
Start-Process -FilePath ".\server_webrtc.exe" -NoNewWindow
cd ..

# 3. Start React UI Dev Server
Write-Output "Starting React UI Dev Server..."
cd react_ui
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -NoNewWindow
cd ..

Write-Output "=== E2E System Started Successfully! ==="
