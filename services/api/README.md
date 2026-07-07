# ATLAS API Gateway Service (`atlas-api`)

Backend API gateway and system orchestrator for the **ATLAS** system.

## Architecture

This service conforms to Clean Architecture, Hexagonal Architecture (Ports and Adapters), and Modular Monolith structure:

- **Presentation Layer**: Exposes API endpoints and manages routers.
- **Application Layer**: orchestrates commands, queries, and domain workflows.
- **Infrastructure Layer**: Manages database adapters, persistence, and external stadium integrations.
- **Shared Package**: Holds centralized logging, configuration settings, and utility extensions.

## Dependency Injection

Wired dynamically via `dependency-injector` container.

## Local Operations

### Install Backend Dependencies

```bash
pip install -e services/api[dev]
```

### Running the API Server

```bash
uvicorn app.main:app --reload --port 8000
```
