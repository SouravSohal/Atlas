#!/usr/bin/env bash
# ==============================================================================
# ATLAS backend Deployment Script (Idempotent & Robust)
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
  grep "^${var_name}=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'" | tr -d '\r'
}

PROJECT=$(extract_env_var "GOOGLE_CLOUD_PROJECT")
REGION=$(extract_env_var "GOOGLE_CLOUD_REGION")
FIRESTORE_DATABASE=$(extract_env_var "FIRESTORE_DATABASE")

if [ -z "$PROJECT" ]; then
  log_error "GOOGLE_CLOUD_PROJECT is not set in the .env file."
  exit 1
fi

REGION=${REGION:-"us-central1"}
FIRESTORE_DATABASE=${FIRESTORE_DATABASE:-"(default)"}

log_info "Configuration loaded:"
echo "  - GCP Project: $PROJECT"
echo "  - GCP Region:  $REGION"
echo "  - Database:    $FIRESTORE_DATABASE"

# Ensure active project is set in gcloud config
log_info "Setting active GCP project to: $PROJECT"
gcloud config set project "$PROJECT" --quiet

# Enable required APIs
log_info "Verifying required GCP Services are enabled..."
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  --quiet

# 3. Prepare Artifact Registry Repository
REPO_NAME="atlas-repo"
log_info "Verifying Artifact Registry repository: $REPO_NAME..."
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" &> /dev/null; then
  log_info "Creating repository $REPO_NAME in location $REGION..."
  gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Docker repository for ATLAS Services" \
    --quiet
else
  log_info "Repository $REPO_NAME exists."
fi

# Configure docker auth for regional registry
log_info "Configuring Docker authentication..."
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

# 4. Build and Push Image
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT/$REPO_NAME/atlas-api:latest"
log_info "Building ATLAS backend image: $IMAGE_TAG..."
docker build -t "$IMAGE_TAG" -f services/api/Dockerfile .

log_info "Pushing image to registry..."
docker push "$IMAGE_TAG"

# 5. Cloud Run Deploy
log_info "Deploying backend service to Google Cloud Run..."
SA_EMAIL="atlas-runtime-sa@$PROJECT.iam.gserviceaccount.com"

# Create service account if not exists
if ! gcloud iam service-accounts describe "$SA_EMAIL" &> /dev/null; then
  log_info "Creating runtime service account: $SA_EMAIL"
  gcloud iam service-accounts create atlas-runtime-sa \
    --display-name="ATLAS Cloud Run Runtime Service Account" \
    --quiet
fi

# Assign Datastore User role to Service Account for Firestore access
log_info "Binding Firestore permissions to runtime service account..."
gcloud projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/datastore.user" \
  --quiet

# Assign Secret Manager Accessor role to Service Account for Secrets access
log_info "Binding Secret Manager permissions to runtime service account..."
gcloud projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor" \
  --quiet

SECRETS_MAP="JWT_SECRET=ATLAS_JWT_SECRET:latest,DEMO_EMAIL=ATLAS_DEMO_EMAIL:latest,DEMO_PASSWORD=ATLAS_DEMO_PASSWORD:latest,FIREBASE_WEB_API_KEY=ATLAS_FIREBASE_API_KEY:latest,GEMINI_API_KEY=ATLAS_GEMINI_API_KEY:latest"

if gcloud run services describe atlas-api --region="$REGION" &> /dev/null; then
  log_info "Backend service atlas-api already exists. Performing safe upgrade..."
  gcloud run deploy atlas-api \
    --image="$IMAGE_TAG" \
    --region="$REGION" \
    --platform=managed \
    --service-account="$SA_EMAIL" \
    --set-env-vars="ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$PROJECT,FIRESTORE_DATABASE=$FIRESTORE_DATABASE" \
    --set-secrets="$SECRETS_MAP" \
    --quiet
else
  log_info "Backend service does not exist. Initializing fresh deployment..."
  gcloud run deploy atlas-api \
    --image="$IMAGE_TAG" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --service-account="$SA_EMAIL" \
    --port=8000 \
    --min-instances=1 \
    --max-instances=10 \
    --set-env-vars="ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$PROJECT,FIRESTORE_DATABASE=$FIRESTORE_DATABASE" \
    --set-secrets="$SECRETS_MAP" \
    --quiet
fi

BACKEND_URL=$(gcloud run services describe atlas-api --region="$REGION" --format="value(status.url)")
log_info "ATLAS backend successfully deployed to: $BACKEND_URL"
