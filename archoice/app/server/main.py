"""ARCHOICE backend — FastAPI.

Endpoints:
  GET  /health           -> liveness + whether a Claude key is configured
  POST /diagnose         -> {image_b64?, media_type?, note?} -> Diagnosis
  POST /plan             -> Diagnosis -> Plan + labeled recommendation slots

Run:
  pip install -r requirements.txt
  uvicorn main:app --reload --host 0.0.0.0 --port 8000

Set ANTHROPIC_API_KEY to use real Claude diagnosis; without it the server returns
honest, labeled stubs (stub=true) so the full loop runs with no key and no hardware.

The web AR client (../web/index.html) is served at / for one-command demos.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from diagnosis import run_diagnose, run_plan
from models import Diagnosis, DiagnoseResponse, PlanResponse

app = FastAPI(title="ARCHOICE API", version="0.1.0")

# Permissive CORS for the demo client (a phone browser hitting the dev server).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


class DiagnoseRequest(BaseModel):
    image_b64: str | None = None
    media_type: str = "image/jpeg"
    note: str = ""


@app.get("/health")
def health() -> dict:
    return {"ok": True, "claude_configured": bool(os.environ.get("ANTHROPIC_API_KEY"))}


@app.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(req: DiagnoseRequest) -> DiagnoseResponse:
    diag, stub = run_diagnose(req.image_b64, req.media_type, req.note)
    return DiagnoseResponse(diagnosis=diag, stub=stub)


@app.post("/plan", response_model=PlanResponse)
def plan(diag: Diagnosis) -> PlanResponse:
    p, recs, stub = run_plan(diag)
    return PlanResponse(plan=p, recommendations=recs, stub=stub)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")
