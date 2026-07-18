#!/usr/bin/env bash
# ==============================================================================
# ATLAS Deployment Verification Script
# ==============================================================================

set -eo pipefail

log_info() {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}

log_error() {
  echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
}

ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
  log_error ".env configuration file is missing at repository root."
  exit 1
fi

extract_env_var() {
  local var_name=$1
  grep "^${var_name}=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r'
}

PROJECT=$(extract_env_var "GOOGLE_CLOUD_PROJECT")
REGION=$(extract_env_var "GOOGLE_CLOUD_REGION")

if [ -z "$PROJECT" ]; then
  log_error "GOOGLE_CLOUD_PROJECT is not set in the .env file."
  exit 1
fi

REGION=${REGION:-"us-central1"}

log_info "Verifying services status in project $PROJECT, region $REGION..."
gcloud config set project "$PROJECT" --quiet &>/dev/null

# 1. Verify Backend
log_info "----------------------------------------"
log_info "Checking Backend Service [atlas-api]..."
if ! gcloud run services describe atlas-api --region="$REGION" &>/dev/null; then
  log_error "Backend service [atlas-api] does not exist!"
else
  BACKEND_URL=$(gcloud run services describe atlas-api --region="$REGION" --format="value(status.url)")
  ACTIVE_REV=$(gcloud run services describe atlas-api --region="$REGION" --format="value(status.latestReadyRevisionName)")
  log_info "Backend URL: $BACKEND_URL"
  log_info "Active Revision: $ACTIVE_REV"

  # Perform health check ping
  HEALTH_URL="$BACKEND_URL/health"
  log_info "Pinging health endpoint: $HEALTH_URL..."
  
  HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || true)
  if [ "$HEALTH_STATUS" -eq 200 ]; then
    log_info "Backend health check PASSED (HTTP 200)"
  else
    log_error "Backend health check FAILED (HTTP status: $HEALTH_STATUS)"
  fi
fi

# 2. Verify Frontend
log_info "----------------------------------------"
log_info "Checking Frontend Service [atlas-frontend]..."
if ! gcloud run services describe atlas-frontend --region="$REGION" &>/dev/null; then
  log_error "Frontend service [atlas-frontend] does not exist!"
else
  FRONTEND_URL=$(gcloud run services describe atlas-frontend --region="$REGION" --format="value(status.url)")
  ACTIVE_REV_FE=$(gcloud run services describe atlas-frontend --region="$REGION" --format="value(status.latestReadyRevisionName)")
  log_info "Frontend URL: $FRONTEND_URL"
  log_info "Active Revision: $ACTIVE_REV_FE"

  # Perform health check ping
  log_info "Pinging frontend home URL..."
  FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || true)
  if [ "$FRONTEND_STATUS" -eq 200 ]; then
    log_info "Frontend availability check PASSED (HTTP 200)"
  else
    log_error "Frontend availability check FAILED (HTTP status: $FRONTEND_STATUS)"
  fi
fi

log_info "----------------------------------------"
log_info "Verification complete."
