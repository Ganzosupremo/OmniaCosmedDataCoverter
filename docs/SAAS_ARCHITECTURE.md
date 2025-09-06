# Phase Analyzer SaaS Architecture

This document outlines a proposed architecture for converting the existing
COSMED XML Data Converter into a multi-tenant Software-as-a-Service.

## Services

- **web**: Streamlit frontend for uploads and basic plan awareness.
- **api**: FastAPI backend exposing health checks and entitlement queries.
- **worker**: RQ worker that will execute long-running batch jobs.
- **redis**: Message broker and task queue backend.
- **db**: PostgreSQL database for users, subscriptions and jobs.

Additional infrastructure such as object storage (S3 compatible) and
email delivery should be added when integrating full functionality.

## Development

Local development is orchestrated through `docker-compose`:

```bash
docker compose up --build
```

This spins up the web app on <http://localhost:8501> and the API on
<http://localhost:8000>.

## Plan Limits

Plan limits are defined in `services/common/config.py` and may be
overridden by environment variables, e.g. `PLAN_PRO_MAX_FILES`.

## Next Steps

1. Implement file uploads to S3 and signed download links.
2. Persist user and job information to PostgreSQL using an ORM.
3. Connect existing batch processing logic from `xml_data_reader` and
   `excel_exporter` inside worker tasks.
4. Integrate Stripe for paid plans and webhook handling.
5. Add notification emails on job completion.
6. Expand tests and add CI for linting and type checking.
