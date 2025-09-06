from fastapi import FastAPI

app = FastAPI(title="Phase Analyzer API")


@app.get("/health")
async def health() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok"}
