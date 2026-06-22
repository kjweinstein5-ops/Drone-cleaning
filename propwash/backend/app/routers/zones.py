"""Zone-related API endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from propwash.backend.models.zone import ZoneSignature
from propwash.backend.safety.checks import SafetyChecker

router = APIRouter()
_safety = SafetyChecker()


@router.get("/{zone_id}", response_model=ZoneSignature)
async def get_zone(zone_id: str):
    # TODO(PROPWASH): wire to DB
    raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found (DB not yet wired)")
