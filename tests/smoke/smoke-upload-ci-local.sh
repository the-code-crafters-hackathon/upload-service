#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PORT="${SMOKE_PORT:-18081}"
BASE_URL="http://127.0.0.1:${PORT}"
WORK_DIR="$(mktemp -d)"
LOG_FILE="$WORK_DIR/upload-smoke.log"
PID_FILE="$WORK_DIR/upload-smoke.pid"

cleanup() {
  set +e
  if [[ -f "$PID_FILE" ]]; then
    PID="$(cat "$PID_FILE")"
    kill "$PID" >/dev/null 2>&1 || true
    wait "$PID" >/dev/null 2>&1 || true
  fi
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

cd "$ROOT_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "[ERRO] curl não encontrado no PATH"
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERRO] python3 não encontrado no PATH"
  exit 2
fi

if ! python3 -c "import uvicorn" >/dev/null 2>&1; then
  echo "[ERRO] uvicorn não está instalado no ambiente atual"
  exit 2
fi

export APP_ENV=development
export AWS_REGION="${AWS_REGION:-us-east-1}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export DATABASE_URL="sqlite:///$WORK_DIR/smoke-upload.db"
export SQLALCHEMY_DATABASE_URL="$DATABASE_URL"
export SQS_VIDEO_PROCESSING_QUEUE="${SQS_VIDEO_PROCESSING_QUEUE:-http://localhost:4566/000000000000/video-processing-queue}"

python3 -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" >"$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

for _ in $(seq 1 30); do
  if curl -fsS "$BASE_URL/health/" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "$BASE_URL/health/" >/dev/null 2>&1; then
  echo "[ERRO] Upload service não subiu a tempo"
  cat "$LOG_FILE"
  exit 1
fi

INVALID_FILE="$WORK_DIR/invalid.txt"
VALID_FILE="$WORK_DIR/test.mp4"
echo "conteudo invalido" > "$INVALID_FILE"
printf 'fake mp4 content for smoke local\n' > "$VALID_FILE"

health_code=$(curl -sS -o "$WORK_DIR/health.json" -w '%{http_code}' "$BASE_URL/health/")
health_db_code=$(curl -sS -o "$WORK_DIR/health_db.json" -w '%{http_code}' "$BASE_URL/health/db")

invalid_code=$(curl -sS -o "$WORK_DIR/upload_invalid.json" -w '%{http_code}' \
  -X POST "$BASE_URL/upload/video" \
  -F "user_id=1" \
  -F "title=invalid-ext" \
  -F "file=@${INVALID_FILE};type=text/plain")

valid_code=$(curl -sS -o "$WORK_DIR/upload_valid.json" -w '%{http_code}' \
  -X POST "$BASE_URL/upload/video" \
  -F "user_id=1" \
  -F "title=smoke-local" \
  -F "file=@${VALID_FILE};type=video/mp4")

if [[ "$health_code" != "200" || "$health_db_code" != "200" || "$invalid_code" != "400" || "$valid_code" != "201" ]]; then
  echo "[ERRO] Smoke local falhou"
  echo "health=$health_code health_db=$health_db_code invalid=$invalid_code valid=$valid_code"
  echo "health body: $(cat "$WORK_DIR/health.json")"
  echo "health db body: $(cat "$WORK_DIR/health_db.json")"
  echo "invalid body: $(cat "$WORK_DIR/upload_invalid.json")"
  echo "valid body: $(cat "$WORK_DIR/upload_valid.json")"
  cat "$LOG_FILE"
  exit 1
fi

echo "[OK] Smoke local do upload concluído com sucesso"