# RAG Pipeline Demo (Portfolio)

This repository is a **reduced public demo of a real project**, prepared for portfolio review.
It keeps real backend engineering concerns (WebSocket chat flow, background jobs, Redis/Postgres integration, retries, circuit-breaker, tests), while trimming non-essential business domain parts.

For architecture details see `ARCHITECTURE.md`.

## Demo Credentials

Use this test account in the UI:

- Login: `demo@domain.com`
- Password: `demo`

## Stack

- Backend: FastAPI + SQLModel + Celery
- Data: PostgreSQL (with pgvector) + Redis
- Pipelines: Haystack-based indexing/search
- Frontend: React
- Infra: Docker Compose

## Quick Start

1. Ensure Docker and Docker Compose are available.
2. Fill `.env`.
3. Start services:

```bash
docker compose up --build
```

After startup:

- open `http://localhost:8001`,
- sign in with the demo credentials above,
- upload/update documents in **Documents**,
- run questions in **Chat**.

## Service Endpoints

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:8001`
- OpenAPI docs: `http://localhost:8000/docs`

## Run Tests

```bash
docker exec haystack pytest -q
```

Static checks:

```bash
docker exec haystack mypy /code
docker exec haystack pyright /code
```

## Database Access

Open PostgreSQL shell inside container:

```bash
docker exec -it postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Connect to test DB:

```sql
\c tests
```

Useful commands:

```sql
\dt
SELECT * FROM public.users;
SELECT * FROM public.documents;
SELECT * FROM public.tokens;
```

## Notes

- This is not a toy “hello world” sample; it is a production-inspired subset of a real system.
- The demo intentionally keeps a single-role model (`user`) and a reduced chat state machine (`answering -> test`) to focus on core backend quality.
- The public demo intentionally focuses on:
  - document management,
  - chat interaction,
  - token accounting,
  - resilience patterns,
  - automated tests.
- Some business-specific entities from the original system were intentionally removed for portfolio clarity.
