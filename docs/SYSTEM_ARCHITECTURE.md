# ATLAS System Architecture

**Project:** ATLAS (Adaptive Tournament Logistics & Autonomous Stadium Intelligence)

**Version:** 1.0

**Status:** Approved

**Architecture Style:** Modular Monolith

**Pattern:** Clean Architecture + Domain Driven Design + Event Driven

---

# 1. Purpose

This document defines the complete software architecture of ATLAS.

It serves as the single source of truth for:

- Backend Engineers
- Frontend Engineers
- AI Engineers
- DevOps Engineers
- AI Coding Agents (Antigravity)

All implementation MUST conform to this architecture.

---

# 2. Architecture Principles

ATLAS follows these principles:

- Domain First
- AI Augmented, not AI Driven
- Context over Raw Data
- Event Driven
- Modular by Capability
- Infrastructure Independent
- Cloud Native
- Secure by Design
- Accessibility by Default
- Explainable AI

---

# 3. Architecture Overview

ATLAS is composed of five logical layers.

```

```
┌─────────────────────────────────────────────────────────┐
│                 EXPERIENCE LAYER                        │
│                                                         │
│ Fan Portal                                              │
│ Volunteer Portal                                        │
│ Operations Dashboard                                    │
│ Executive Dashboard                                     │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                APPLICATION LAYER                        │
│                                                         │
│ Use Cases                                               │
│ Workflow Orchestration                                  │
│ API Controllers                                         │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│               INTELLIGENCE LAYER                        │
│                                                         │
│ AI Orchestrator                                         │
│ Prompt Builder                                          │
│ Context Retrieval                                       │
│ Gemini                                                  │
│ Validator                                               │
│ Recommendation Engine                                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   DOMAIN LAYER                          │
│                                                         │
│ Operational State                                       │
│ Events                                                  │
│ Recommendations                                         │
│ Tasks                                                   │
│ Incidents                                               │
│ Business Rules                                          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE LAYER                       │
│                                                         │
│ Firestore                                               │
│ Firebase Auth                                           │
│ Cloud Run                                               │
│ Maps                                                    │
│ Translation                                             │
│ Speech                                                  │
│ Secret Manager                                          │
│ Monitoring                                              │
└─────────────────────────────────────────────────────────┘
```

---

# 4. High Level System

```
Users

↓

React Applications

↓

FastAPI API

↓

Application Layer

↓

Domain Layer

↓

Repository Interfaces

↓

Infrastructure

↓

Google Cloud
```

No component may bypass the Domain Layer.

---

# 5. Core Components

## Experience Layer

Responsible for all user interfaces.

Contains:

- Fan Workspace
- Volunteer Workspace
- Operations Workspace
- Executive Workspace

Responsibilities:

- Rendering UI
- Authentication
- Displaying Operational State
- User Interaction

No business logic.

---

## Application Layer

Responsible for orchestration.

Contains:

- Use Cases
- Services
- Controllers

Responsibilities:

- Coordinate workflows
- Execute business use cases
- Publish Domain Events
- Call AI Orchestrator

No persistence logic.

---

## Intelligence Layer

Responsible for all AI capabilities.

Contains:

- AI Orchestrator
- Prompt Builder
- Context Retriever
- Recommendation Generator
- Prediction Generator
- Validator

Responsibilities:

- Build prompts
- Retrieve operational context
- Invoke Gemini
- Validate outputs
- Return structured responses

Never directly accesses Firestore.

---

## Domain Layer

The heart of the application.

Contains:

Entities

- User
- Event
- Incident
- Task
- Recommendation
- OperationalState

Value Objects

- Coordinates
- QueueEstimate
- CrowdDensity
- Route

Repositories

Interfaces only.

Business Rules

Domain Events

Policies

No framework dependencies.

---

## Infrastructure Layer

Responsible for external systems.

Contains:

- Firestore
- Firebase Authentication
- Google Maps
- Translation API
- Speech API
- Cloud Storage
- Cloud Logging
- Secret Manager

Implements repository interfaces.

---

# 6. Operational State

The Operational State is the single source of truth.

Every operation updates it.

Every AI request reads from it.

Every dashboard displays it.

```
Sensors

↓

Domain Events

↓

Operational State

↓

AI

↓

Recommendation

↓

Human Approval

↓

Execution

↓

Operational State
```

---

# 7. Domain Events

Every important action becomes an event.

Examples:

- CrowdDensityChanged
- IncidentCreated
- GateOpened
- VolunteerAssigned
- RecommendationGenerated
- RecommendationApproved
- RouteUpdated
- WeatherUpdated

Events are immutable.

---

# 8. AI Pipeline

All AI requests follow the same pipeline.

```
Request

↓

Retrieve Operational State

↓

Retrieve Knowledge

↓

Build Prompt

↓

Gemini

↓

Validator

↓

Confidence Score

↓

Recommendation

↓

Audit Log

↓

Response
```

Every AI capability MUST use this pipeline.

---

# 9. Request Lifecycle

```
Client

↓

Authentication

↓

Authorization

↓

Validation

↓

Controller

↓

Use Case

↓

Domain

↓

Repository

↓

Infrastructure

↓

Response
```

---

# 10. Event Lifecycle

```
Event Created

↓

Validation

↓

Domain Event

↓

Operational State Update

↓

AI Analysis

↓

Recommendation

↓

Approval

↓

Execution

↓

Audit Log
```

---

# 11. Service Boundaries

Application Services

- Incident Service
- Navigation Service
- Notification Service
- Recommendation Service
- Analytics Service

Infrastructure Services

- Firestore Repository
- Maps Adapter
- Translation Adapter
- Gemini Adapter

No Application Service may directly call another service's persistence.

---

# 12. Repository Pattern

Repositories belong to the Domain.

Implementations belong to Infrastructure.

Example

Domain

```
RecommendationRepository
```

Infrastructure

```
FirestoreRecommendationRepository
```

Never expose Firestore outside Infrastructure.

---

# 13. Dependency Rules

Allowed

```
Experience

↓

Application

↓

Domain

↓

Infrastructure
```

Forbidden

```
Domain → Infrastructure

Infrastructure → Application

Experience → Infrastructure

Experience → Gemini
```

---

# 14. Google Cloud Architecture

```
React

↓

Cloud Run

↓

FastAPI

↓

Firestore

↓

Cloud Storage

↓

Gemini

↓

Maps

↓

Translation

↓

Speech

↓

Monitoring
```

---

# 15. Security Model

Authentication

↓

Authorization

↓

Input Validation

↓

Business Rules

↓

Repository

↓

Audit Logging

↓

Response

Every request follows this sequence.

---

# 16. Observability

Every service must provide

- Structured Logging
- Metrics
- Tracing
- Health Endpoint
- Error Reporting

---

# 17. Fault Tolerance

If AI fails

↓

Business Rules continue

If Maps fails

↓

Fallback Navigation

If Translation fails

↓

Original Language

The platform should degrade gracefully.

---

# 18. Architecture Decisions

ADR-001

Architecture

Modular Monolith

Status

Accepted

---

ADR-002

Pattern

Clean Architecture

Status

Accepted

---

ADR-003

Domain Strategy

Domain Driven Design

Status

Accepted

---

ADR-004

Deployment

Google Cloud Run

Status

Accepted

---

ADR-005

Database

Firestore

Status

Accepted

---

ADR-006

AI

Gemini 2.5

Status

Accepted

---

ADR-007

Authentication

Firebase Authentication

Status

Accepted

---

ADR-008

Single Source of Truth

Operational State

Status

Accepted

---

ADR-009

Communication

Internal Domain Events

Status

Accepted

---

ADR-010

AI Integration

AI Orchestrator

Status

Accepted

---

# 19. Non-Negotiable Rules

1. Domain contains no framework code.

2. AI never bypasses Domain.

3. Firestore never leaks into business logic.

4. Every feature starts with a Use Case.

5. Every state change emits a Domain Event.

6. AI recommendations require validation.

7. High-impact actions require human approval.

8. Everything is testable.

9. Every module has one responsibility.

10. Architecture consistency takes priority over development speed.

---

# 20. Implementation Order

1. Repository Initialization

2. Domain Layer

3. Repository Interfaces

4. Firestore Implementations

5. Application Layer

6. FastAPI

7. Authentication

8. AI Orchestrator

9. Frontend

10. Deployment

Implementation MUST follow this order.
