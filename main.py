"""
SentinelAI Lightweight Gateway Proxy for Render Free Tier
---------------------------------------------------------
This featherweight proxy forwards queries to the Hugging Face Space:
https://huggingface.co/spaces/NOT-OMEGA/SentinelAI

Memory footprint: ~25MB RAM (Under 5% of Render's 512MB free tier).
No C++ compiler, No PyTorch, No heavy ML models on Render.
"""

import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

HF_SPACE_URL = os.getenv("HF_SPACE_URL", "https://not-omega-sentinelai.hf.space").rstrip("/")

app = FastAPI(
    title="SentinelAI-RAG Gateway (Render Proxy)",
    description="Lightweight edge proxy for Hugging Face Space backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_index():
    """Serve the frosted glass Apple UI chat interface."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        index_file = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": "SentinelAI Proxy is running. Static UI not found."})


@app.get("/health")
@app.get("/v1/health")
async def health_check():
    """Health check verifying upstream connection to Hugging Face Space."""
    upstream_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{HF_SPACE_URL}/v1/health")
            upstream_status = "connected" if resp.status_code == 200 else f"status_{resp.status_code}"
    except Exception as e:
        upstream_status = f"unreachable ({str(e)})"

    return {
        "status": "healthy",
        "service": "SentinelAI-Render-Proxy",
        "mode": "edge-proxy",
        "upstream_hf_space": HF_SPACE_URL,
        "upstream_status": upstream_status
    }


@app.post("/v1/rag/query")
async def proxy_rag_query(request: Request):
    """
    Forward RAG queries from user frontend directly to Hugging Face Space.
    Preserves all headers (BYOK keys, provider selection) and payload.
    """
    body = await request.body()
    forward_headers = {}
    for h in ["content-type", "x-user-provider", "x-user-model", "x-user-api-key", "authorization"]:
        val = request.headers.get(h)
        if val:
            forward_headers[h] = val

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            upstream_resp = await client.post(
                f"{HF_SPACE_URL}/v1/rag/query",
                content=body,
                headers=forward_headers
            )
            return Response(
                content=upstream_resp.content,
                status_code=upstream_resp.status_code,
                media_type=upstream_resp.headers.get("content-type", "application/json")
            )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=504,
            content={"detail": "Upstream Hugging Face Space query timed out after 60s."}
        )
    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={"detail": f"Failed to forward request to Hugging Face Space: {str(exc)}"}
        )


@app.post("/v1/cache/clear")
async def proxy_cache_clear(request: Request):
    """Forward semantic cache flush to Hugging Face Space."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream_resp = await client.post(f"{HF_SPACE_URL}/v1/cache/clear")
            return Response(
                content=upstream_resp.content,
                status_code=upstream_resp.status_code,
                media_type=upstream_resp.headers.get("content-type", "application/json")
            )
    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={"detail": f"Cache flush failed: {str(exc)}"}
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
