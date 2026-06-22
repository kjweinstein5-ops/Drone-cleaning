"""Job and work-order API endpoints + WebSocket telemetry stream."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from propwash.backend.models.work_order import WorkOrder, WorkOrderStatus
from propwash.backend.models.verification import VerificationResult

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory stores — replace with DB queries
_work_orders: Dict[str, WorkOrder] = {}
_verifications: Dict[str, List[VerificationResult]] = {}
_ws_clients: List[WebSocket] = []


async def _broadcast(event: Dict[str, Any]) -> None:
    dead = []
    for ws in _ws_clients:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ws_clients.remove(ws)


@router.get("", response_model=List[WorkOrder])
async def list_jobs():
    return list(_work_orders.values())


@router.get("/{job_id}", response_model=WorkOrder)
async def get_job(job_id: str):
    if job_id not in _work_orders:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return _work_orders[job_id]


@router.post("/{job_id}/status", response_model=WorkOrder)
async def update_job_status(job_id: str, body: Dict[str, Any]):
    if job_id not in _work_orders:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    wo = _work_orders[job_id]
    new_status = WorkOrderStatus(body.get("status", wo.status))
    updated = wo.model_copy(update={"status": new_status})
    _work_orders[job_id] = updated
    await _broadcast({"event": "job_status", "job_id": job_id, "status": new_status})
    return updated


@router.get("/{job_id}/verifications", response_model=List[VerificationResult])
async def get_verifications(job_id: str):
    return _verifications.get(job_id, [])


@router.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    await websocket.accept()
    _ws_clients.append(websocket)
    logger.info("WebSocket telemetry client connected (%d total)", len(_ws_clients))
    try:
        while True:
            # Keep connection alive; server pushes events via _broadcast
            await websocket.receive_text()
    except WebSocketDisconnect:
        _ws_clients.remove(websocket)
        logger.info("WebSocket client disconnected (%d remaining)", len(_ws_clients))
