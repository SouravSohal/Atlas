# ATLAS

> **Adaptive Tournament Logistics & Autonomous Stadium Intelligence**

ATLAS is an AI-powered Operational Intelligence Platform built for the FIFA World Cup 2026.

Rather than being another chatbot or navigation application, ATLAS continuously understands the operational state of a stadium and assists fans, volunteers, operators, security teams, and executives through real-time recommendations, predictive analytics, and intelligent coordination.

---

# Vision

Build the world's most intelligent stadium operations platform using Google Cloud and Generative AI.

---

# Key Capabilities

- 🧭 Intelligent Indoor Navigation
- 👥 Crowd Intelligence
- 🚨 Incident Management
- 🤖 AI Decision Support
- 🌍 Multilingual Assistance
- ♿ Accessibility Support
- 📢 Smart Notifications
- 📊 Executive Analytics
- 🏟 Operational Intelligence

---

# Architecture

ATLAS follows:

- Modular Monolith
- Clean Architecture
- Domain Driven Design
- Event Driven Architecture
- AI Orchestrator Pattern

See:

- docs/SYSTEM_ARCHITECTURE.md
- docs/ENGINEERING_GUIDE.md
- docs/IMPLEMENTATION_PLAN.md

---

# Technology Stack

## Frontend

- React
- TypeScript
- Vite
- TailwindCSS
- TanStack Query

## Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- Uvicorn

## AI

- Gemini 2.5
- Google ADK
- Vertex AI

## Cloud

- Cloud Run
- Firestore
- Firebase Authentication
- Cloud Storage
- Secret Manager
- Cloud Logging
- Cloud Monitoring

---

# Repository Structure

```
atlas/

apps/
packages/
services/
infrastructure/
docs/
scripts/
```

---

# Getting Started

## 1. Database Configuration
ATLAS connects to a Google Cloud Firestore instance in development and production:
- **GCP Project ID**: `atlas-501808`
- **Firestore Database Name**: `atlas-01`

Make sure your local environment is configured by duplicating `.env.example` as `.env` and supplying your local credentials if necessary.

## 2. Running the Backend
You can boot the FastAPI backend server using the configured startup script in the `scripts` folder:
```bash
./scripts/run_backend.sh
```
Alternatively, execute the command directly from the workspace root:
```bash
FIRESTORE_DATABASE=atlas-01 GOOGLE_CLOUD_PROJECT=atlas-501808 PYTHONPATH=services/api/src:packages/atlas-core/src .venv/bin/python -m uvicorn services.api.src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 3. Running the Frontend
Navigate to the frontend dashboard package and run Vite:
```bash
cd apps/operations-dashboard
npm run dev
```

For a comprehensive guide, read the documentation files in this order:
1. `PRD.md`
2. `SYSTEM_ARCHITECTURE.md`
3. `ENGINEERING_GUIDE.md`
4. `IMPLEMENTATION_PLAN.md`

---

# Development Principles

- Domain First
- AI Assisted
- Test Driven
- Security First
- Accessibility First

---

# License

Private Repository.