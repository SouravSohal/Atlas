#!/usr/bin/env bash
# ==============================================================================
# ATLAS Frontend Deployment Script (Idempotent & Robust)
# ==============================================================================

set -eo pipefail

# Helper to print colored status messages
log_info() {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}

log_error() {
  echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
}

# 1. Prerequisite Validations
log_info "Validating prerequisites..."

if ! command -v gcloud &> /dev/null; then
  log_error "Google Cloud CLI (gcloud) is not installed. Please install it."
  exit 1
fi

if ! command -v docker &> /dev/null; then
  log_error "Docker is not installed. Please install it."
  exit 1
fi

if ! docker info &> /dev/null; then
  log_error "Docker daemon is not running. Please start Docker."
  exit 1
fi

# Check if authenticated with gcloud
if ! gcloud auth list --filter=status=ACTIVE --format="value(account)" | grep -q "@"; then
  log_error "Not authenticated with gcloud. Please run 'gcloud auth login'."
  exit 1
fi

# 2. Parse Environment Configuration
log_info "Loading environment settings from .env file..."
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
  log_error ".env configuration file is missing at repository root."
  exit 1
fi

extract_env_var() {
  local var_name=$1
  local target_file=${2:-$ENV_FILE}
  grep "^${var_name}=" "$target_file" | cut -d'=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r'
}

PROJECT=$(extract_env_var "GOOGLE_CLOUD_PROJECT")
REGION=$(extract_env_var "GOOGLE_CLOUD_REGION")

if [ -z "$PROJECT" ]; then
  log_error "GOOGLE_CLOUD_PROJECT is not set in the .env file."
  exit 1
fi

REGION=${REGION:-"us-central1"}

log_info "Configuration loaded:"
echo "  - GCP Project: $PROJECT"
echo "  - GCP Region:  $REGION"

# Ensure active project is set in gcloud config
gcloud config set project "$PROJECT" --quiet

# Verify backend service exists and retrieve status URL
log_info "Retrieving backend URL from Cloud Run..."
BACKEND_URL=$(gcloud run services describe atlas-api --region="$REGION" --format="value(status.url)" 2>/dev/null || true)

if [ -z "$BACKEND_URL" ]; then
  log_error "Backend service atlas-api is not deployed or unreachable in region $REGION. Deploy backend first."
  exit 1
fi
log_info "Target backend API URL: $BACKEND_URL"

# Extract Firebase configuration from frontend .env
FRONTEND_ENV="apps/operations-dashboard/.env"
if [ ! -f "$FRONTEND_ENV" ]; then
  log_error "Frontend environment file is missing: $FRONTEND_ENV"
  exit 1
fi

log_info "Extracting build arguments from $FRONTEND_ENV..."
FIREBASE_API_KEY=$(extract_env_var "VITE_FIREBASE_API_KEY" "$FRONTEND_ENV")
FIREBASE_AUTH_DOMAIN=$(extract_env_var "VITE_FIREBASE_AUTH_DOMAIN" "$FRONTEND_ENV")
FIREBASE_PROJECT_ID=$(extract_env_var "VITE_FIREBASE_PROJECT_ID" "$FRONTEND_ENV")
FIREBASE_STORAGE_BUCKET=$(extract_env_var "VITE_FIREBASE_STORAGE_BUCKET" "$FRONTEND_ENV")
FIREBASE_MESSAGING_SENDER_ID=$(extract_env_var "VITE_FIREBASE_MESSAGING_SENDER_ID" "$FRONTEND_ENV")
FIREBASE_APP_ID=$(extract_env_var "VITE_FIREBASE_APP_ID" "$FRONTEND_ENV")
DEMO_EMAIL=$(extract_env_var "VITE_DEMO_EMAIL" "$FRONTEND_ENV")
DEMO_PASSWORD=$(extract_env_var "VITE_DEMO_PASSWORD" "$FRONTEND_ENV")

# 3. Build and Push Image
REPO_NAME="atlas-repo"
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT/$REPO_NAME/atlas-frontend:latest"

log_info "Building ATLAS frontend production image: $IMAGE_TAG..."
docker build -t "$IMAGE_TAG" \
  --build-arg VITE_API_BASE_URL="$BACKEND_URL" \
  --build-arg VITE_FIREBASE_API_KEY="$FIREBASE_API_KEY" \
  --build-arg VITE_FIREBASE_AUTH_DOMAIN="$FIREBASE_AUTH_DOMAIN" \
  --build-arg VITE_FIREBASE_PROJECT_ID="$FIREBASE_PROJECT_ID" \
  --build-arg VITE_FIREBASE_STORAGE_BUCKET="$FIREBASE_STORAGE_BUCKET" \
  --build-arg VITE_FIREBASE_MESSAGING_SENDER_ID="$FIREBASE_MESSAGING_SENDER_ID" \
  --build-arg VITE_FIREBASE_APP_ID="$FIREBASE_APP_ID" \
  --build-arg VITE_DEMO_EMAIL="$DEMO_EMAIL" \
  --build-arg VITE_DEMO_PASSWORD="$DEMO_PASSWORD" \
  -f apps/operations-dashboard/Dockerfile .

log_info "Pushing image to registry..."
docker push "$IMAGE_TAG"

# 4. Cloud Run Deploy
log_info "Deploying frontend service to Google Cloud Run..."

if gcloud run services describe atlas-frontend --region="$REGION" &> /dev/null; then
  log_info "Frontend service atlas-frontend already exists. Performing safe upgrade, preserving configurations..."
  gcloud run deploy atlas-frontend \
    --image="$IMAGE_TAG" \
    --region="$REGION" \
    --platform=managed \
    --quiet
else
  log_info "Frontend service does not exist. Initializing fresh deployment..."
  gcloud run deploy atlas-frontend \
    --image="$IMAGE_TAG" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --min-instances=1 \
    --max-instances=10 \
    --quiet
fi

FRONTEND_URL=$(gcloud run services describe atlas-frontend --region="$REGION" --format="value(status.url)")
log_info "ATLAS frontend successfully deployed to: $FRONTEND_URL"
