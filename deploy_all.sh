#!/usr/bin/env bash
# ==============================================================================
# ATLAS Unified Deployment Script (Idempotent & Robust)
# ==============================================================================

set -eo pipefail

log_info() {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}

log_error() {
  echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
}

log_info "=========================================="
log_info "ATLAS Platform Deployment Pipeline Start"
log_info "=========================================="

# 1. Deploy Backend
log_info "Deploying Backend API Gateway..."
if ! ./deploy_backend.sh; then
  log_error "Backend deployment failed. Aborting pipeline."
  exit 1
fi

# 2. Deploy Frontend
log_info "Deploying Frontend Operations Dashboard..."
if ! ./deploy_frontend.sh; then
  log_error "Frontend deployment failed. Aborting pipeline."
  exit 1
fi

# 3. Resolve CORS by updating Backend with Frontend URL
ENV_FILE=".env"
extract_env_var() {
  local var_name=$1
  grep "^${var_name}=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r'
}
PROJECT=$(extract_env_var "GOOGLE_CLOUD_PROJECT")
REGION=$(extract_env_var "GOOGLE_CLOUD_REGION")
REGION=${REGION:-"asia-south2"}

log_info "Retrieving frontend and backend URLs for CORS configuration..."
gcloud config set project "$PROJECT" --quiet &>/dev/null
FRONTEND_URL=$(gcloud run services describe atlas-frontend --region="$REGION" --format="value(status.url)" 2>/dev/null || true)

if [ -n "$FRONTEND_URL" ]; then
  log_info "Frontend URL: $FRONTEND_URL"
  log_info "Updating backend CORS origins to allow: $FRONTEND_URL..."
  gcloud run services update atlas-api \
    --update-env-vars="^;^API_CORS_ORIGINS=http://localhost:5173,$FRONTEND_URL" \
    --region="$REGION" \
    --quiet
  log_info "CORS origins successfully configured!"
else
  log_error "Could not retrieve frontend URL. CORS configuration skipped."
fi

# 4. Verify Deployment
log_info "Executing deployment verifications..."
if ! ./verify_deployment.sh; then
  log_error "Deployment verification failed. Please check services logs."
  exit 1
fi

log_info "=========================================="
log_info "ATLAS Platform Deployment Completed Successfully!"
log_info "=========================================="
