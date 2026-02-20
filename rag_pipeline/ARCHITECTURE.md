# Architecture

## Purpose

This repository contains a reduced demo version of a real RAG/chat backend + frontend stack.
The code is intentionally trimmed for portfolio review, but keeps real production patterns:

- FastAPI backend
- WebSocket chat session pipeline
- PostgreSQL + pgvector
- Redis memory/state
- Celery background jobs
- React frontend

## High-Level Components

- `source/backend/main.py`
  - FastAPI app entrypoint, router registration, lifespan startup.
- `source/backend/routes/`
  - HTTP/WebSocket API layer (`auth`, `me`, `documents`, `chat`).
- `source/backend/services/`
  - Application/service logic.
  - `chat_session/` manages chat runtime, stages, delivery, recovery.
  - `celery_tasks/` contains async background work (tokens, indexing, summaries, context).
  - `haystack/` contains document indexing/search integration.
- `source/backend/models/`
  - SQLModel ORM + Pydantic schemas.
  - Core entities: user, document, chat passport/log/snapshot/context, token stats.
- `source/backend/db/`
  - DB init and migrations.
- `source/frontend/`
  - React UI for auth, document management, and chat testing.

## Chat Flow (Current Minimal Version)

1. Client opens WebSocket: `/chat/ws?chat_passport_id=...`
2. User message is pushed to Redis inbox.
3. Chat stage manager processes inbox:
   - `ANSWERING`: RAG search + answer generation
   - `TEST`: free chat mode
4. Messages are sent through `WebSocketDeliveryManager` with retry/buffering.
5. Side effects (tokens/summary/context/chat logs) are persisted via Celery + PostgreSQL/Redis.

## Data Flow

- User/docs/chat metadata: PostgreSQL
- Vector retrieval data: pgvector document store
- Session memory/locks/pending messages: Redis
- Heavy/async post-processing: Celery workers

## Reliability Patterns Present

- Retry wrappers for transient Redis/DB failures
- Circuit breaker behavior around LLM/pipeline calls
- Message buffering + resend logic for WebSocket delivery interruptions
- Advisory lock based serialization for selected Celery chat tasks

## Scope Notes

- This is the intentionally reduced public demo scope.
- Legacy organization/category/bot and multi-role management were removed from runtime domain.
- Existing tests are adapted to this minimal domain while keeping integration behavior (including real WebSocket tests).
