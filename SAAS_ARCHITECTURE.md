# Phase Analyzer SaaS Architecture

This document outlines the initial architecture for running the COSMED Phase Analyzer as a multi-tenant SaaS application.

## Services

| Service | Description |
|---------|-------------|
| `web`   | Streamlit UI for uploads and job creation. |
| `api`   | FastAPI service for health checks, entitlements and Stripe webhooks. |
| `worker`| RQ worker that processes queued jobs and writes outputs to object storage. |
| `redis` | Queue backend used by RQ. |
| `db`    | PostgreSQL database storing users, subscriptions and job metadata. |
| `storage` | S3-compatible bucket for uploaded files and exported results. |

## Local Development

The project includes a `docker-compose.yml` file to run all services locally:

```bash
docker compose up --build
```

Web interface: <http://localhost:8501>

API: <http://localhost:8000/health>

MinIO console: <http://localhost:9001>

## Next Steps

- Implement database models for users, organisations and jobs.
- Connect the existing batch processing core to the `worker` service.
- Add authentication and plan enforcement in the Streamlit frontend.
- Integrate Stripe Checkout and customer portal.
- Send email notifications when a batch job completes.
