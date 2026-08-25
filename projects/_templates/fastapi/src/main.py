"""FastAPI application template for a self-contained daily project."""

from fastapi import FastAPI

app = FastAPI(title="Day XX API", version="0.1.0")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Provide a deterministic endpoint for local verification."""
    return {"status": "ok"}
