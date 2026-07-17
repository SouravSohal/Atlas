# ATLAS Platform Production Deployment Guide

This document describes the containerization structure, Docker build operations, Google Cloud Run deployment procedures, and production environment variables configuration for the ATLAS platform backend API gateway.

---

## 1. Container Architecture

The ATLAS backend uses a multi-stage Docker build to compile and package dependencies securely.

- **Stage 1 (Builder)**: Utilizes a Python base image, installs build tools (`build-essential`), copies the monorepo core package `packages/atlas-core` and the API service `services/api`, and compiles the dependencies with their respective wheel formats to a temporary `/install` directory.
- **Stage 2 (Runner)**: Uses a clean, production-grade `python:3.12-slim` image, copies the compiled binaries from `/install` into `/usr/local` (leaving behind any dev tooling, compiler libraries, and caches), exposes the runtime port, configures non-root system users (`appuser` with UID/GID 10001), and boots using Uvicorn.

---

## 2. Docker Instructions

### Build the Image
To build the Docker image, run the build command from the monorepo root directory (to ensure the local package dependency `atlas-core` is present in the build context):

```bash
docker build -t gcr.io/your-project-id/atlas-api:latest -f services/api/Dockerfile .
```

### Run Locally via Docker
To spin up the container locally for verification, supply your credentials and secrets via environment variables:

```bash
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -e GOOGLE_CLOUD_PROJECT=atlas-501808 \
  -e FIRESTORE_DATABASE=atlas-01 \
  -e JWT_SECRET=your-strong-cryptographically-secure-key \
  -e DEMO_EMAIL=demo@atlas.com \
  -e DEMO_PASSWORD=your-secure-demo-password \
  -e FIREBASE_WEB_API_KEY=your-firebase-web-api-key \
  -v /absolute/path/to/your/service-account.json:/app/credentials.json \
  gcr.io/your-project-id/atlas-api:latest
```

---

## 3. Google Cloud Run Deployment

We deploy the container image directly to Google Cloud Run for serverless, autoscaling execution.

### Step 1: Push the Image to Artifact Registry
Configure credentials and push the built image to your Google Artifact Registry repository:

```bash
# Authenticate gcloud CLI
gcloud auth configure-docker us-central1-docker.pkg.dev

# Tag the image for Artifact Registry
docker tag gcr.io/your-project-id/atlas-api:latest us-central1-docker.pkg.dev/your-project-id/atlas-repo/atlas-api:latest

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
  --set-env-vars="ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=atlas-501808,FIRESTORE_DATABASE=atlas-01" \
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
| `JWT_SECRET` | Secret Manager | Yes | Strong cryptographically secure JWT signing key. |
| `DEMO_EMAIL` | Secret Manager | Yes | Registered demo admin email. |
| `DEMO_PASSWORD` | Secret Manager | Yes | Strong unique password for the demo admin account. |
| `FIREBASE_WEB_API_KEY` | Secret Manager | Yes | Firebase Web API key. Mock placeholder allowed in dev but strictly rejected at startup in Production. |
| `GEMINI_API_KEY` | Secret Manager | Yes (if using AI) | Google Gemini model access key. Mock placeholder allowed in dev but strictly rejected at startup in Production. |
