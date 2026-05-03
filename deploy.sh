#!/bin/bash
set -euo pipefail

# ── Config ────────────────────────────────────────────────
APP_NAME="not-so-local-finance"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PROJECT_DIR="" #directory where the project is located on the server 
N8N_WEBHOOK="" #webhook url for n8n -you can get it from n8n webhook settings after creating workflow 
N8N_SECRET="" #secret for n8n webhook -you can get it from n8n webhook settings after creating workflow 
LOG_FILE="" #log file for the deployment script 

# ── Logging ───────────────────────────────────────────────
exec >> "$LOG_FILE" 2>&1

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }
die() { log "ERROR: $*"; notify "failure" "$*"; exit 1; }

# ── n8n notification ──────────────────────────────────────
notify() {
  local status="$1"
  local message="${2:-}"

  curl -s -o /dev/null --max-time 5 \
    -X POST "$N8N_WEBHOOK" \
    -H "Content-Type: application/json" \
    -H "X-Deploy-Secret: ${N8N_SECRET}" \
    -d "{
      \"app\":     \"${APP_NAME}\",
      \"status\":  \"${status}\",
      \"message\": \"${message}\",
      \"host\":    \"$(hostname)\",
      \"time\":    \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }" || log "Warning: failed to reach n8n (non-fatal)"
}

# ── Deploy ────────────────────────────────────────────────
log "════════════════════════════════════"
log "Deploy started for ${APP_NAME}"
notify "started"

log "Changing to project directory..."
cd "$PROJECT_DIR" || die "Could not cd into ${PROJECT_DIR}"

log "Pulling latest code..."
git pull origin main || die "git pull failed"

log "Restarting containers..."
docker compose up -d --build --remove-orphans || die "docker compose up failed"

log "Cleaning up old images..."
docker image prune -f > /dev/null

log "Deploy finished successfully"
notify "success" "Containers are up and running"