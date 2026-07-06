# ATLAS Engineering Guide

**Project:** ATLAS

**Version:** 1.0

**Status:** Approved

---

# Purpose

This document defines engineering standards for ATLAS.

Every engineer and AI coding assistant must follow these rules.

The objective is:

- Consistent code
- Maintainability
- Security
- Scalability
- Testability

---

# Engineering Philosophy

ATLAS follows:

- Clean Architecture
- Domain Driven Design (DDD)
- SOLID Principles
- DRY
- KISS
- Composition over Inheritance
- Explicit over Implicit

---

# Development Principles

## 1. Domain First

Business logic is the heart of the application.

Everything else supports it.

Priority:

Domain

↓

Application

↓

Infrastructure

↓

UI

---

## 2. AI is an Enhancement

AI must never contain business rules.

Business Rules

↓

AI Recommendation

↓

Validation

↓

Execution

---

## 3. Modular by Capability

Never organize by technology.

❌ Bad

backend/

controllers/

models/

utils/

services/

Good

services/

navigation/

events/

analytics/

notifications/

---

## 4. One Responsibility

Every module has exactly one responsibility.

If a file performs multiple unrelated tasks,

split it.

---

# Repository Structure

atlas/

apps/

fan-web/

operations-dashboard/

volunteer-portal/

packages/

atlas-core/

shared/

contracts/

schemas/

ui/

services/

api/

.github/

docs/

scripts/

---

# Python Standards

Python Version

3.12+

Mandatory

- Type Hints
- Async
- Pydantic v2
- Ruff
- Black
- MyPy

Formatting

Line Length

100

Indentation

4 spaces

Quotes

Double Quotes

---

# FastAPI Rules

Use

- APIRouter
- Dependency Injection
- Pydantic Models
- Async Endpoints

Never

- Business Logic in Controllers
- Firestore Calls in Controllers
- AI Calls in Controllers

Controller

↓

Use Case

↓

Repository

↓

Infrastructure

---

# TypeScript Standards

Version

Latest Stable

Mandatory

Strict Mode

No implicit any

ESLint

Prettier

Functional Components

Hooks

Never use class components.

---

# React Architecture

Feature First

features/

navigation/

dashboard/

recommendations/

notifications/

Each feature contains

components/

hooks/

services/

types/

pages/

---

# Naming Conventions

Classes

PascalCase

RecommendationService

Variables

camelCase

recommendationScore

Constants

UPPER_SNAKE_CASE

MAX_QUEUE_SIZE

Files

snake_case.py

kebab-case.tsx

Interfaces

Prefix with I only if language requires it.

---

# Folder Responsibilities

Domain

Pure business logic

Application

Use Cases

Infrastructure

Firestore

Maps

Gemini

Storage

Presentation

API

React

---

# Dependency Rules

Allowed

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Forbidden

Domain → Infrastructure

Presentation → Firestore

Presentation → Gemini

Application → Firestore

---

# Dependency Injection

Every external dependency

must be injected.

Never instantiate services directly.

Bad

service = RecommendationService()

Good

Depends(get_recommendation_service)

---

# Repository Pattern

Domain owns interfaces.

Infrastructure implements them.

Example

Domain

RecommendationRepository

Infrastructure

FirestoreRecommendationRepository

---

# Error Handling

Never expose raw exceptions.

Always convert

↓

Domain Error

↓

HTTP Error

↓

Structured Response

---

# Logging

Use structured logging.

Every log contains

- timestamp
- request_id
- user_id
- event_id
- severity

Never print().

---

# Configuration

Configuration comes from

Environment Variables

↓

Pydantic Settings

↓

Dependency Injection

Never hardcode

- URLs
- Keys
- IDs
- Secrets

---

# Secrets

All secrets stored in

Google Secret Manager

Never

.env committed

API Keys in source

Secrets in frontend

---

# AI Development Rules

Never send raw user input directly to Gemini.

Pipeline

User Input

↓

Validation

↓

Operational Context

↓

Prompt Builder

↓

Gemini

↓

Validator

↓

Response

All prompts are versioned.

---

# Prompt Engineering

Every prompt must contain

- Role
- Context
- Constraints
- Expected Output
- JSON Schema

No free-form responses.

---

# Function Calling

Gemini never executes actions.

Gemini

↓

Function Suggestion

↓

Validation

↓

Approval

↓

Execution

---

# Firestore Rules

Never access Firestore directly.

Always use repositories.

Never

collection("events")

inside business logic.

---

# Caching

Use caching only in infrastructure.

Business logic should not know caching exists.

---

# Testing Philosophy

Testing Pyramid

End-to-End

↓

Integration

↓

Unit

Target

Unit

90%+

Integration

Critical Workflows

End-to-End

Primary User Journeys

---

# Unit Test Rules

Every Domain Entity

must be tested.

Every Value Object

must be tested.

Every Business Rule

must be tested.

---

# Integration Tests

Test

Firestore

Authentication

Gemini

Maps

Cloud APIs

---

# Accessibility

Must satisfy WCAG 2.2 AA

Keyboard Navigation

Screen Reader

Focus States

High Contrast

Semantic HTML

---

# API Standards

REST

/api/v1/

Response Format

{

success,

data,

metadata,

request_id

}

Never return raw objects.

---

# Documentation

Every public function

must contain

Purpose

Arguments

Returns

Raises

Example

---

# Pull Request Checklist

- Builds successfully

- Lint passes

- Formatting passes

- Type checks pass

- Tests pass

- Documentation updated

- No duplicated logic

- Security reviewed

- Accessibility reviewed

---

# Performance

Async by default

Avoid blocking IO

Reuse connections

Batch reads where possible

Avoid unnecessary Firestore reads

---

# Security

JWT Authentication

RBAC

Input Validation

Output Sanitization

Audit Logging

Rate Limiting

OWASP Top 10

---

# Observability

Every service exposes

/health

Structured Logs

Metrics

Tracing

Error Reporting

---

# Definition of Done

Feature is complete only if

✓ Requirements implemented

✓ Tests pass

✓ Security reviewed

✓ Documentation updated

✓ Accessible

✓ Logged

✓ Monitored

✓ Deployable

---

# AI Coding Rules (Antigravity)

Before writing code

Always

1. Read SYSTEM_ARCHITECTURE.md

2. Follow Clean Architecture

3. Never bypass Domain Layer

4. Write tests

5. Use dependency injection

6. Produce production-quality code

7. Explain architectural decisions if deviating

Never

- Duplicate code

- Ignore typing

- Hardcode values

- Mix responsibilities

- Break dependency rules

---

# Engineering Motto

Architecture over Speed.

Consistency over Cleverness.

Quality over Quantity.

Readable over Concise.

Simple over Complex.

Always optimize for long-term maintainability.
