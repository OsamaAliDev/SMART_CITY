from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str = "viewer"

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Incidents
class IncidentBase(BaseModel):
    subsystem: str = Field(..., pattern="^(smart_home|autonomous_car|smart_train|ev_charging|smart_parking|warehouse)$")
    title: str
    description: Optional[str] = None
    severity: str = Field("medium", pattern="^(low|medium|high|critical)$")
    status: str = Field("active", pattern="^(active|resolved)$")

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(active|resolved)$")

class IncidentOut(IncidentBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None

    model_config = {"from_attributes": True}

# Telemetry
class TelemetryBase(BaseModel):
    subsystem: str = Field(..., pattern="^(smart_home|autonomous_car|smart_train|ev_charging|smart_parking|warehouse)$")
    metric_key: str
    metric_value: float
    unit: Optional[str] = None

class TelemetryCreate(TelemetryBase):
    pass

class TelemetryOut(TelemetryBase):
    id: int
    recorded_at: datetime

    model_config = {"from_attributes": True}

# Audit logs
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}