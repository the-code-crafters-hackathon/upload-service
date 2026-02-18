#!/usr/bin/env bash
set -euo pipefail

if ! command -v curl >/dev/null 2>&1; then
  echo "[ERRO] curl não encontrado no PATH"
  exit 2
fi

AWS_REGION="${AWS_REGION:-us-east-1}"
ALB_NAME="${ALB_NAME:-hackathon-alb}"
ALB_DNS="${ALB_DNS:-}"
ECS_CLUSTER_NAME="${ECS_CLUSTER_NAME:-}"
ECS_SERVICE_NAME="${ECS_SERVICE_NAME:-}"
UPLOAD_USER_ID="${UPLOAD_USER_ID:-1}"
UPLOAD_TITLE="${UPLOAD_TITLE:-smoke-video}"
EXPECT_VALID_STATUS="${EXPECT_VALID_STATUS:-201}"

resolve_alb_dns_from_ecs() {
  local tg_arn=""
  local lb_arn=""
  local dns=""

  if [[ -z "${ECS_CLUSTER_NAME:-}" || -z "${ECS_SERVICE_NAME:-}" ]]; then
    return 1
  fi

  tg_arn=$(aws ecs describe-services \
    --cluster "$ECS_CLUSTER_NAME" \
    --services "$ECS_SERVICE_NAME" \
    --region "$AWS_REGION" \
    --query 'services[0].loadBalancers[0].targetGroupArn' \
    --output text 2>/dev/null || true)

  if [[ -z "$tg_arn" || "$tg_arn" == "None" ]]; then
    return 1
  fi

  lb_arn=$(aws elbv2 describe-target-groups \
    --target-group-arns "$tg_arn" \
    --region "$AWS_REGION" \
    --query 'TargetGroups[0].LoadBalancerArns[0]' \
    --output text 2>/dev/null || true)

  if [[ -z "$lb_arn" || "$lb_arn" == "None" ]]; then
    return 1
  fi

  dns=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns "$lb_arn" \
    --region "$AWS_REGION" \
    --query 'LoadBalancers[0].DNSName' \
    --output text 2>/dev/null || true)

  if [[ -z "$dns" || "$dns" == "None" ]]; then
    return 1
  fi

  echo "$dns"
  return 0
}

if [[ -z "$ALB_DNS" ]]; then
  if ! command -v aws >/dev/null 2>&1; then
    echo "[ERRO] aws cli não encontrada e ALB_DNS não foi informado"
    exit 2
  fi

  if resolved_dns=$(resolve_alb_dns_from_ecs); then
    ALB_DNS="$resolved_dns"
  else
    ALB_DNS=$(aws elbv2 describe-load-balancers \
      --names "$ALB_NAME" \
      --region "$AWS_REGION" \
      --query 'LoadBalancers[0].DNSName' \
      --output text)
  fi
fi

if [[ -z "$ALB_DNS" || "$ALB_DNS" == "None" ]]; then
  echo "[ERRO] Não foi possível resolver ALB_DNS (ALB_NAME=$ALB_NAME, AWS_REGION=$AWS_REGION)"
  exit 2
fi

BASE_URL="http://${ALB_DNS}"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

INVALID_FILE="$WORK_DIR/invalid.txt"
VALID_FILE="$WORK_DIR/test.mp4"

echo "conteudo invalido" > "$INVALID_FILE"
printf 'fake mp4 content for smoke test\n' > "$VALID_FILE"

PASS_COUNT=0
FAIL_COUNT=0

check_status() {
  local name="$1"
  local got="$2"
  local expected="$3"
  if [[ "$got" == "$expected" ]]; then
    echo "[PASS] $name -> $got"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "[FAIL] $name -> esperado=$expected obtido=$got"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

request_code() {
  local method="$1"
  local url="$2"
  local output_file="$3"
  shift 3
  curl -sS -o "$output_file" -w '%{http_code}' -X "$method" "$url" "$@"
}

echo "[INFO] Base URL: $BASE_URL"

a_health_body="$WORK_DIR/health.json"
a_health_db_body="$WORK_DIR/health_db.json"
a_invalid_body="$WORK_DIR/upload_invalid.json"
a_valid_body="$WORK_DIR/upload_valid.json"

code_health=$(request_code GET "$BASE_URL/health/" "$a_health_body")
check_status "GET /health/" "$code_health" "200"

code_health_db=$(request_code GET "$BASE_URL/health/db" "$a_health_db_body")
check_status "GET /health/db" "$code_health_db" "200"

code_invalid=$(request_code POST "$BASE_URL/upload/video" "$a_invalid_body" \
  -F "user_id=${UPLOAD_USER_ID}" \
  -F "title=invalid-ext" \
  -F "file=@${INVALID_FILE};type=text/plain")
check_status "POST /upload/video (ext inválida)" "$code_invalid" "400"

code_valid=$(request_code POST "$BASE_URL/upload/video" "$a_valid_body" \
  -F "user_id=${UPLOAD_USER_ID}" \
  -F "title=${UPLOAD_TITLE}" \
  -F "file=@${VALID_FILE};type=video/mp4")
check_status "POST /upload/video (ext válida)" "$code_valid" "$EXPECT_VALID_STATUS"

echo ""
echo "[RESUMO] PASS=$PASS_COUNT FAIL=$FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  echo "[DETALHE] /health/: $(head -c 220 "$a_health_body" | tr '\n' ' ')"
  echo "[DETALHE] /health/db: $(head -c 220 "$a_health_db_body" | tr '\n' ' ')"
  echo "[DETALHE] upload inválido: $(head -c 220 "$a_invalid_body" | tr '\n' ' ')"
  echo "[DETALHE] upload válido: $(head -c 300 "$a_valid_body" | tr '\n' ' ')"
  exit 1
fi

echo "[OK] Smoke test de upload concluído com sucesso"