from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from database import get_db
from models import Incident, User
from schemas import IncidentCreate, IncidentUpdate, IncidentOut
from auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("/", response_model=List[IncidentOut])
def list_incidents(
    subsystem: Optional[str] = Query(None, regex="^(smart_home|autonomous_car|smart_train|ev_charging|smart_parking|warehouse)$"),
    status: Optional[str] = Query(None, regex="^(active|resolved)$"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Incident)
    if subsystem:
        query = query.filter(Incident.subsystem == subsystem)
    if status:
        query = query.filter(Incident.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/", response_model=IncidentOut, status_code=201)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_incident = Incident(**incident.dict(), resolved_by=None)
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

@router.put("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    update_data = incident_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_incident, key, value)
    db.commit()
    db.refresh(db_incident)
    return db_incident

@router.post("/{incident_id}/resolve", response_model=IncidentOut)
def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if db_incident.status == "resolved":
        raise HTTPException(status_code=400, detail="Incident already resolved")
    db_incident.status = "resolved"
    db_incident.resolved_at = datetime.utcnow()
    db_incident.resolved_by = current_user.id
    db.commit()
    db.refresh(db_incident)
    return db_incident

@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    db.delete(db_incident)
    db.commit()
    return None