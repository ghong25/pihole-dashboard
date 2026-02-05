#!/usr/bin/env bash
set -euo pipefail

PI_HOST="${PI_HOST:-ghong@192.168.1.10}"
PI_DIR="/home/ghong/pihole-dashboard"

echo "==> Building frontend..."
cd "$(dirname "$0")/frontend"
npm install
npm run build
cd ..

echo "==> Syncing project to Pi..."
rsync -avz --delete \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude 'frontend/node_modules' \
  --exclude 'backend/venv' \
  --exclude 'backend/__pycache__' \
  --exclude 'backend/app/__pycache__' \
  --exclude 'backend/dashboard.db' \
  ./ "${PI_HOST}:${PI_DIR}/"

echo "==> Setting up Python venv on Pi..."
ssh "${PI_HOST}" "cd ${PI_DIR}/backend && \
  (test -d venv || python3 -m venv venv) && \
  venv/bin/pip install -q -r requirements.txt"

echo "==> Installing systemd service..."
ssh "${PI_HOST}" "sudo cp ${PI_DIR}/pihole-dashboard.service /etc/systemd/system/ && \
  sudo systemctl daemon-reload && \
  sudo systemctl enable pihole-dashboard && \
  sudo systemctl restart pihole-dashboard"

echo "==> Checking service status..."
ssh "${PI_HOST}" "sudo systemctl status pihole-dashboard --no-pager" || true

echo ""
echo "==> Done! Dashboard available at http://192.168.1.10:8080"
