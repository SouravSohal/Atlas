# ATLAS Platform Production Deployment Guide

This document describes the containerization structure, Docker build operations, Google Cloud Run deployment procedures, and production environment variables configuration for the ATLAS platform backend API gateway.

---

## 1. Container Architecture

The ATLAS backend uses a multi-stage Docker build to compile and package dependencies securely.

- **Stage 1 (Builder)**: Utilizes a Python base image, installs build tools (`build-essential`), copies the monorepo core package `packages/atlas-core` and the API service `services/api`, builds local `.whl` wheels for both into `/build/wheels`, and installs them.
- **Stage 2 (Runner)**: Uses a clean, production-grade `python:3.12-slim` image, copies the compiled binaries from `/install` into `/usr/local` (leaving behind any dev tooling, compiler libraries, and caches), exposes the runtime port, configures non-root system users (`appuser` with UID/GID 10001), and boots using Uvicorn.

---

## 2. Local Docker Development & Commands

To manage the API gateway locally via Docker, follow these instructions using the environment configuration file `.env.docker` at the repository root.

### Build the Image
Build the Docker image from the monorepo root directory:
```bash
docker build -t atlas-api:latest -f services/api/Dockerfile .
```

### Run the Container
Run the container locally by loading environment variables from `.env.docker` and mounting your Google Cloud service account JSON credentials to `/app/credentials.json`:
```bash
docker run -d \
  --name atlas-api \
  -p 8080:8000 \
  --env-file .env.docker \
  -v /absolute/path/to/your/gcp-service-account.json:/app/credentials.json \
  atlas-api:latest
```

### Docker Management Commands

- **View Logs**:
  ```bash
  docker logs -f atlas-api
  ```
- **Stop the Container**:
  ```bash
  docker stop atlas-api
  ```
- **Remove the Container**:
  ```bash
  docker rm atlas-api
  ```
- **Rebuild the Container (Clean cache & rebuild)**:
  ```bash
  docker build --no-cache -t atlas-api:latest -f services/api/Dockerfile .
  ```

### Verify Endpoints

- **Health Endpoint**:
  ```bash
  curl -f http://localhost:8080/health
  ```
- **Readiness Endpoint**:
  ```bash
  curl -f http://localhost:8080/ready
  ```

---

## 3. Google Cloud Run Deployment

We deploy the container image directly to Google Cloud Run for serverless, autoscaling execution.

### Cloud Run Authentication Architecture
Unlike local Docker executions, **Google Cloud Run does NOT require the `GOOGLE_APPLICATION_CREDENTIALS` environment variable or a mounted Service Account key JSON file.**
Instead:
1. Assign a dedicated **Runtime Service Account** to the Cloud Run service.
2. Grant that Service Account appropriate IAM permissions (e.g. `roles/datastore.user` for Firestore access, `roles/secretmanager.secretAccessor` for Secret Manager).
3. Cloud Run automatically uses the GCP **Metadata Server** to fetch and authenticate service account tokens at runtime, completely eliminating key file management.

### Step 1: Push the Image to Artifact Registry
Configure credentials and push the built image to your Google Artifact Registry repository:
```bash
# Authenticate gcloud CLI
gcloud auth configure-docker us-central1-docker.pkg.dev

# Tag the image for Artifact Registry
docker tag atlas-api:latest us-central1-docker.pkg.dev/your-project-id/atlas-repo/atlas-api:latest

# Push the image
docker push us-central1-docker.pkg.dev/your-project-id/atlas-repo/atlas-api:latest
```

### Step 2: Deploy to Google Cloud Run
Deploy the container with CPU/memory configurations, IAM service account, and environment configuration:
```bash
gcloud run deploy atlas-api \
  --image=us-central1-docker.pkg.dev/your-project-id/atlas-repo/atlas-api:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --service-account=atlas-runtime-sa@your-project-id.iam.gserviceaccount.com \
  --port=8000 \
  --min-instances=1 \
  --max-instances=10 \
  --set-env-vars="ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=your-project-id,FIRESTORE_DATABASE=your-database-name" \
  --set-secrets="JWT_SECRET=JWT_SECRET:latest,DEMO_EMAIL=DEMO_EMAIL:latest,DEMO_PASSWORD=DEMO_PASSWORD:latest,FIREBASE_WEB_API_KEY=FIREBASE_WEB_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest"
```

---

## 4. Production Environment Variables & Secrets Checklist

Use Google Secret Manager to mount sensitive values rather than injecting them in plain text:

| Environment Variable | Source / Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `PORT` | Managed by Cloud Run | Yes | Port the container listens on (Defaults to `8000`). |
| `ENVIRONMENT` | String (`production` / `staging`) | Yes | Operational environment target. |
| `GOOGLE_CLOUD_PROJECT` | GCP Managed / Environment | Yes | GCP Project ID (e.g. `atlas-501808`). |
| `FIRESTORE_DATABASE` | Environment | Yes | Firestore Database instance name (e.g. `atlas-01`). |
| `API_CORS_ORIGINS` | Environment | No | Comma-separated list of allowed origins (e.g. `https://atlas-frontend-1017580106397.asia-south2.run.app`). |
| `JWT_SECRET` | Secret Manager | Yes | Strong cryptographically secure JWT signing key. |
| `DEMO_EMAIL` | Secret Manager | Yes | Registered demo admin email. |
| `DEMO_PASSWORD` | Secret Manager | Yes | Strong unique password for the demo admin account. |
| `FIREBASE_WEB_API_KEY` | Secret Manager | Yes | Firebase Web API key. Mock placeholder allowed in dev but strictly rejected at startup in Production. |
| `GEMINI_API_KEY` | Secret Manager | Yes (if using AI) | Google Gemini model access key. Mock placeholder allowed in dev but strictly rejected at startup in Production. |

### 4.1. Frontend Build-Time variables (Vite Build Arguments)

These variables must be passed during the frontend container build stage via Docker `--build-arg`:

| Build Argument / Env Var | Required | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Yes | Target backend API gateway base URL. |
| `VITE_DEMO_EMAIL` | Yes | Seeded demo user email address. |
| `VITE_DEMO_PASSWORD` | Yes | Seeded demo user password. |
| `VITE_FIREBASE_API_KEY` | Yes | Firebase Web Client API key. |
| `VITE_FIREBASE_AUTH_DOMAIN` | Yes | Firebase Auth domain (e.g. `atlas-501808.firebaseapp.com`). |
| `VITE_FIREBASE_PROJECT_ID` | Yes | Firebase Project ID (e.g. `atlas-501808`). |
| `VITE_FIREBASE_STORAGE_BUCKET`| Yes | Firebase Storage bucket. |
| `VITE_FIREBASE_MESSAGING_SENDER_ID`| Yes | Firebase Messaging Sender ID. |
| `VITE_FIREBASE_APP_ID` | Yes | Firebase App Client ID. |

---

## 5. Troubleshooting Startup Failures

If the container fails to start, verify logs by running `docker logs atlas-api` or checking Cloud Logging in GCP. Common errors include:

- **Missing JWT Secret (`ValidationError` / `Secret key cannot be empty`)**:
  * **Cause**: `JWT_SECRET` is not set in `.env.docker` or GCP configuration.
  * **Fix**: Ensure `JWT_SECRET` is populated with a string of at least 32 characters.
- **Missing Gemini API Key / Firebase Key in Production**:
  * **Cause**: Running with `ENVIRONMENT=production` while `GEMINI_API_KEY` or `FIREBASE_WEB_API_KEY` is empty, missing, or matches mock/development placeholders.
  * **Fix**: Configure valid, non-placeholder keys inside GCP Secret Manager or your production environment settings.
- **Firestore Authentication Failures**:
  * **Cause**: Either `GOOGLE_APPLICATION_CREDENTIALS` points to an invalid path locally, or the Cloud Run Runtime Service Account is missing the `roles/datastore.user` IAM role.
  * **Fix**: Locally, confirm your service account key file is correctly mounted. In GCP, verify IAM bindings.
- **Missing Seed Data (`RuntimeError: Startup validation failed: Stadium seed data file is missing`)**:
  * **Cause**: The stadium seed data JSON file is missing or `DEMO__SEED_DATA_PATH` is incorrect.
  * **Fix**: Verify `stadium_seed_data.json` is packaged within `atlas-stadium-core` or mount/configure `DEMO__SEED_DATA_PATH` explicitly.
- **Invalid Environment Variables (`ValueError: Invalid environment value`)**:
  * **Cause**: `ENVIRONMENT` is set to an unsupported value.
  * **Fix**: Set `ENVIRONMENT` to either `development` or `production` strictly.
