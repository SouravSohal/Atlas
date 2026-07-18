#!/usr/bin/env bash
# ==============================================================================
# ATLAS Cloud Run Revision Rollback Script (Idempotent & Robust)
# ==============================================================================

set -eo pipefail

log_info() {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}

log_error() {
  echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
}

# 1. Parse Arguments
SERVICE=${1:-"atlas-api"}

if [ "$SERVICE" != "atlas-api" ] && [ "$SERVICE" != "atlas-frontend" ]; then
  log_error "Invalid service name. Must be either 'atlas-api' or 'atlas-frontend'."
  exit 1
fi

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

log_info "Initiating rollback procedure for service [$SERVICE] in project $PROJECT, region $REGION..."
gcloud config set project "$PROJECT" --quiet &>/dev/null

# 2. Retrieve Revisions List
log_info "Fetching revisions for $SERVICE..."
# Retrieve revisions ordered by creation time (newest first)
# gcloud returns metadata.name lists. We grab the top two.
mapfile -t REVS < <(gcloud run revisions list --service="$SERVICE" --region="$REGION" --sort-by="~metadata.creationTimestamp" --format="value(metadata.name)" | head -n 5)

if [ ${#REVS[@]} -lt 2 ]; then
  log_error "Not enough revisions found to perform a rollback. At least 2 revisions are required."
  exit 1
fi

CURRENT_REV=${REVS[0]}
PREVIOUS_REV=${REVS[1]}

log_info "Active Revision:   $CURRENT_REV"
log_info "Target Rollback Revision: $PREVIOUS_REV"

# 3. Apply Rollback via update-traffic
log_info "Shifting 100% traffic to previous revision $PREVIOUS_REV..."
gcloud run services update-traffic "$SERVICE" \
  --to-revisions="$PREVIOUS_REV=100" \
  --region="$REGION" \
  --quiet

log_info "Rollback successful. Service [$SERVICE] is now routing traffic to $PREVIOUS_REV."
