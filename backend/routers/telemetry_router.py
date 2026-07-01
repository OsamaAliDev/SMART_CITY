from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Telemetry, User
from schemas import TelemetryCreate, TelemetryOut
from auth import get_current_user

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.post("/ingest", response_model=TelemetryOut, status_code=201)
def ingest_telemetry(
    telemetry: TelemetryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_telemetry = Telemetry(**telemetry.dict())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

@router.get("/latest", response_model=List[TelemetryOut])
def get_latest_telemetry(
    subsystem: Optional[str] = Query(None, pattern="^(smart_home|autonomous_car|smart_train|ev_charging|smart_parking|warehouse)$"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Telemetry)
    if subsystem:
        query = query.filter(Telemetry.subsystem == subsystem)
    query = query.order_by(Telemetry.recorded_at.desc()).limit(limit)
    return query.all()

@router.get("/history", response_model=List[TelemetryOut])
def get_telemetry_history(
    subsystem: str = Query(..., pattern="^(smart_home|autonomous_car|smart_train|ev_charging|smart_parking|warehouse)$"),
    metric_key: str = Query(...),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    استرجاع البيانات التاريخية لمتريك معين ونظام معين، مرتبة تنازلياً حسب الوقت.
    """
    query = db.query(Telemetry).filter(
        Telemetry.subsystem == subsystem,
        Telemetry.metric_key == metric_key
    ).order_by(Telemetry.recorded_at.desc()).limit(limit)
    return query.all()