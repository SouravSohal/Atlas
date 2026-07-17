# ATLAS Platform Runtime Validation Checklist

This checklist provides a step-by-step verification procedure to confirm that the ATLAS API gateway has been correctly containerized, configured, and deployed, and that all core capabilities function in both local Docker and production Google Cloud Run environments.

---

## 1. Build and Deployment Verification

- [ ] **Docker Image Builds**:
  * Build the Docker image from the monorepo root:
    ```bash
    docker build -t atlas-api:latest -f services/api/Dockerfile .
    ```
  * Confirm the build exits with status `0` and compiles the `atlas-stadium-core` wheel locally without requesting PyPI.
- [ ] **Container Starts**:
  * Run the container (or start via `docker compose up -d`) using `.env.docker`:
    ```bash
    docker run -d --name atlas-api -p 8080:8000 --env-file .env.docker -v /path/to/local/gcp-key.json:/app/credentials.json atlas-api:latest
    ```
  * Monitor startup logs to confirm the Uvicorn server is bound:
    ```bash
    docker logs -f atlas-api
    ```
- [ ] **Production Startup Validation**:
  * Run the container with `ENVIRONMENT=production` and mock credentials (e.g. `FIREBASE_WEB_API_KEY=mock-firebase-key-replace-in-production`).
  * Verify the container **fails immediately** on startup with a descriptive `RuntimeError`.

---

## 2. Infrastructure & Integration Health

- [ ] **Health Endpoint (`/health`)**:
  * Perform a GET request to `/health`.
  * Verify it returns `200 OK` and structured JSON status containing `"healthy"`.
- [ ] **Readiness Endpoint (`/ready`)**:
  * Perform a GET request to `/ready`.
  * Verify it returns `200 OK` indicating downstream systems are connected.
- [ ] **Firestore Connectivity**:
  * During startup (in non-pytest runs), verify logs show `Database connectivity check passed successfully`.
  * Verify collection reads do not time out or fail with IAM permission issues.
- [ ] **Firebase Authentication**:
  * Attempt to call the `/auth/login` endpoint with valid credentials.
  * Verify token validation works, custom claims (`role`) are checked statelessly, and it returns valid access/refresh tokens.
- [ ] **Gemini Connectivity**:
  * In non-mock environments, trigger a request utilizing generative models (such as situation briefings or copilot).
  * Confirm that logs show successful calls to Google GenAI without authentication failures.

---

## 3. Core Capability Checks

- [ ] **Demo Login**:
  * Verify that a POST request to `/auth/login` using the demo email/password succeeds and extracts appropriate claims (lowest fallback to `fan` if claims are missing).
- [ ] **Digital Twin (Operational State)**:
  * Fetch current stadium digital twin state from the `/dashboard/state` or `/stadium/state` routes.
  * Ensure the payload parses correct zone maps, incident states, and operational profiles.
- [ ] **Timeline (Briefings)**:
  * Fetch intelligence briefings and timeline narratives from `/dashboard/briefings`.
  * Ensure response caching serves subsequent requests within the configured TTL.
- [ ] **Recommendations**:
  * Trigger crowd management recommendations from `/dashboard/recommendations`.
  * Confirm that recommendations populate correctly.
- [ ] **Copilot assistant**:
  * Open a WebSocket handshake or POST query to `/copilot/query`.
  * Check that context-aware AI support returns valid suggestions.
- [ ] **Executive Room (Dashboard Metrics)**:
  * Fetch executive stadium operational metrics from `/dashboard/metrics`.
  * Confirm metrics are correctly aggregated.

---

## 4. Operational Readiness

- [ ] **Graceful Shutdown**:
  * Stop the container:
    ```bash
    docker stop atlas-api
    ```
  * Verify in logs that the Firestore connection pool closes gracefully:
    ```
    Closed Firestore AsyncClient connection
    ```
- [ ] **Structured Logging**:
  * In production mode, verify stdout lines are parsed as valid, single-line structured JSON records containing timestamps, levels, and correlation fields.
