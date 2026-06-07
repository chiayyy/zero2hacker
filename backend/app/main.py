from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, StreamingResponse
import uvicorn
import os
import httpx
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="Zero2Hacker CTF Platform",
    description="AI-driven adaptive CTF platform for cybersecurity education",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files for challenge resources at /files to avoid CRA dev proxy conflict
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/files", StaticFiles(directory=str(static_path)), name="static")

# Security
security = HTTPBearer()


@app.get("/")
async def root():
    return {
        "message": "Welcome to Zero2Hacker CTF Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "zero2hacker-backend"}


ALLOWED_CHALLENGE_PORTS = {8080, 8081, 8082, 8083, 8084, 8085, 8086, 8087}

@app.api_route("/challenge/{port}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def challenge_proxy(port: int, path: str, request: Request):
    """Proxy requests to challenge apps so they work through the Cloudflare tunnel."""
    if port not in ALLOWED_CHALLENGE_PORTS:
        raise HTTPException(status_code=403, detail="Port not allowed")

    target_url = f"http://127.0.0.1:{port}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=False,
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Challenge app not running. Click Launch Challenge first.")

    # Rewrite redirect Location headers to go through proxy
    resp_headers = dict(resp.headers)
    if "location" in resp_headers:
        loc = resp_headers["location"]
        if loc.startswith("/"):
            resp_headers["location"] = f"/challenge/{port}{loc}"
    resp_headers.pop("transfer-encoding", None)
    resp_headers.pop("content-encoding", None)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=resp_headers,
        media_type=resp.headers.get("content-type"),
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )