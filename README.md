# ATLAS - Smart Stadiums & Tournament Operations

> **Adaptive Tournament Logistics & Autonomous Stadium Intelligence**

ATLAS is an AI-powered Operational Intelligence Platform built for the FIFA World Cup 2026, targeting the **Smart Stadiums & Tournament Operations** vertical.

---

## 1. Chosen Vertical: Smart Stadiums & Tournament Operations

In large-scale tournaments like the FIFA World Cup, managing stadium operations is complex, involving:
- High-density crowd management and routing.
- Real-time incident detection, escalation, and resolution.
- Coordination of fans, volunteers, and operations teams.
- Context-aware decision intelligence for executives.

ATLAS addresses this vertical by continuously aggregating the stadium's operational state and providing real-time recommendations, predictive analytics, and automated coordination.

---

## 2. Approach and Logic

ATLAS is built using a **Vertical Slice Architecture** structured around **Domain-Driven Design (DDD)** and **Clean Architecture** principles.

- **Domain First**: Core business models, entities (e.g. [Incident](file:///home/kenx1kaneki/Desktop/Codesstuff/Atlas/packages/atlas-core/src/atlas_core/entities/incident.py) and [Recommendation](file:///home/kenx1kaneki/Desktop/Codesstuff/Atlas/packages/atlas-core/src/atlas_core/entities/recommendation.py)), and validation logic are isolated in a framework-agnostic package ([atlas-core](file:///home/kenx1kaneki/Desktop/Codesstuff/Atlas/packages/atlas-core/src/atlas_core/)).
- **Event-Driven Operational State**: Every event (e.g. crowd density update, incident report) updates the global `OperationalState`. 
- **AI Decision Support**: We employ an **AI Orchestrator Pattern** utilizing Gemini. Rather than giving the LLM raw access or execution power, the AI retrieves structured context from the `OperationalState`, builds versioned prompts, suggests validated actions, and requires human approval for high-impact decisions.

---

## 3. How the Solution Works

1. **Ingestion & Processing**:
   - Sensors, volunteers, or mock systems publish domain events.
   - The FastAPI backend updates Firestore and publishes state changes.
2. **Context-Aware Analytics & Predictions**:
   - The backend runs predictive models (e.g. queue estimations, route optimization) to update digital twin telemetry.
3. **AI Copilot & Recommendations**:
   - The AI Orchestrator uses structural schema validations to output JSON-only action suggestions.
4. **Operations Control Center**:
   - Operators monitor live incidents, map coordinates, and AI predictions on the React operations dashboard via real-time WebSocket connections.

---

## 4. Key Assumptions Made

1. **Connectivity**: Stable internet connection is available for Google Cloud Run, Firestore, and Vertex AI (Gemini) API integrations.
2. **Firebase Auth**: User roles (e.g., `operator`, `volunteer`, `fan`) are managed statelessly using custom claims embedded in Firebase ID tokens.
3. **Data Telemetry**: Stadium infrastructure (gates, concessions, zones) publishes regular metrics to construct the operational digital twin.
4. **Human in the Loop**: AI recommendations require explicit operator approval before executing notifications or triggering system changes.

---

## 5. Technology Stack

### Frontend
- React, TypeScript, Vite, TailwindCSS, TanStack Query

### Backend
- Python 3.12+, FastAPI, Pydantic v2, Uvicorn, NetworkX (Graph Engine)

### AI & Infrastructure
- Gemini, Firebase Auth, Firestore, Google Cloud Run, Secret Manager

---

## 6. Getting Started

### 1. Database Configuration
ATLAS connects to a Google Cloud Firestore instance:
- **GCP Project ID**: `atlas-501808`
- **Firestore Database Name**: `atlas-01`

Make sure your local environment is configured by duplicating `.env.example` as `.env` and supplying your local credentials if necessary.

### 2. Running the Backend
Boot the FastAPI backend server:
```bash
./scripts/run_backend.sh
```
Or directly from the workspace root:
```bash
FIRESTORE_DATABASE=atlas-01 GOOGLE_CLOUD_PROJECT=atlas-501808 PYTHONPATH=services/api/src:packages/atlas-core/src .venv/bin/python -m uvicorn services.api.src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Running the Frontend
Navigate to the frontend package and run Vite:
```bash
cd apps/operations-dashboard
npm run dev
```

For a comprehensive guide, read the documentation files in this order:
1. [SYSTEM_ARCHITECTURE.md](file:///home/kenx1kaneki/Desktop/Codesstuff/Atlas/docs/SYSTEM_ARCHITECTURE.md)
2. [ENGINEERING_GUIDE.md](file:///home/kenx1kaneki/Desktop/Codesstuff/Atlas/docs/ENGINEERING_GUIDE.md)
3. [IMPLEMENTATION_PLAN.md](file:///home/kenx1kaneki/Desktop/Codesstuff/Atlas/docs/IMPLEMENTATION_PLAN.md)
4. [DEPLOYMENT.md](file:///home/kenx1kaneki/Desktop/Codesstuff/Atlas/docs/DEPLOYMENT.md)