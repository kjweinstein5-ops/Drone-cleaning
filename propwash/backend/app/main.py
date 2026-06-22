"""PROPWASH FastAPI application — routers + WebSocket telemetry."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from propwash.backend.app.routers import jobs, zones, health

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="PROPWASH Orchestrator API",
    description="AI-orchestrated exterior building-cleaning platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO(PROPWASH): lock down before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(zones.router, prefix="/zones", tags=["zones"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
