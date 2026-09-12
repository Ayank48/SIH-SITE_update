"""
TEAM ZERODAY: SIH26166 Lunar Image Correspondence System
FastAPI Backend Application Entrypoint
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import CORS_ORIGINS, SESSIONS_DIR, SAMPLES_DIR
from backend.api.routers import ingestion, pipeline

app = FastAPI(
    title="TEAM ZERODAY - Lunar Correspondence Platform",
    description="SIH26166: Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ingestion.router)
app.include_router(pipeline.router)

# Mount sessions for binary file access
app.mount("/sessions", StaticFiles(directory=str(SESSIONS_DIR)), name="sessions")


@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "system": "ISRO SIH26166 Lunar Correspondence Engine",
        "team": "TEAM ZERODAY",
        "version": "1.0.0",
        "modules": [
            "Lunar Correspondence Court",
            "Lunar Correspondence DNA",
            "Blind Lunar Test",
            "Lunar Correspondence Graph"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
