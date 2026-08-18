from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AssetClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class AssetType(str, Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    DATA = "data"
    PEOPLE = "people"
    SERVICE = "service"


class RiskStatus(str, Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    TREATED = "treated"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ControlType(str, Enum):
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"


class ImplementationStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    NOT_APPLICABLE = "not_applicable"


class TreatmentType(str, Enum):
    MITIGATE = "mitigate"
    TRANSFER = "transfer"
    ACCEPT = "accept"
    AVOID = "avoid"


class TreatmentStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def calculate_risk_level(likelihood: int, impact: int) -> RiskLevel:
    score = likelihood * impact

    if score <= 4:
        return RiskLevel.LOW
    if score <= 9:
        return RiskLevel.MEDIUM
    if score <= 16:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def validate_score(value: int) -> int:
    if value < 1 or value > 5:
        raise ValueError("O valor deve estar entre 1 e 5.")
    return value


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    database: str


class SettingsResponse(BaseModel):
    application: str
    version: str


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    classification: AssetClassification
    asset_type: AssetType
    owner: str = Field(..., min_length=1, max_length=200)


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    classification: Optional[AssetClassification] = None
    asset_type: Optional[AssetType] = None
    owner: Optional[str] = Field(None, min_length=1, max_length=200)


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Risks
# ---------------------------------------------------------------------------

class RiskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    asset_id: Optional[int] = None
    likelihood: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)
    status: RiskStatus = RiskStatus.IDENTIFIED

    @field_validator("likelihood", "impact")
    @classmethod
    def check_score(cls, value: int) -> int:
        return validate_score(value)


class RiskCreate(RiskBase):
    pass


class RiskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    asset_id: Optional[int] = None
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    impact: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[RiskStatus] = None

    @field_validator("likelihood", "impact")
    @classmethod
    def check_score(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        return validate_score(value)


class RiskResponse(RiskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    risk_level: RiskLevel
    risk_score: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

class ControlBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    risk_id: Optional[int] = None
    control_type: ControlType
    implementation_status: ImplementationStatus = ImplementationStatus.NOT_STARTED
    framework_reference: Optional[str] = Field(None, max_length=100)


class ControlCreate(ControlBase):
    pass


class ControlUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    risk_id: Optional[int] = None
    control_type: Optional[ControlType] = None
    implementation_status: Optional[ImplementationStatus] = None
    framework_reference: Optional[str] = Field(None, max_length=100)


class ControlResponse(ControlBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Treatment actions
# ---------------------------------------------------------------------------

class TreatmentActionBase(BaseModel):
    risk_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    owner: str = Field(..., min_length=1, max_length=200)
    due_date: date
    treatment_type: TreatmentType
    status: TreatmentStatus = TreatmentStatus.OPEN


class TreatmentActionCreate(TreatmentActionBase):
    pass


class TreatmentActionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    owner: Optional[str] = Field(None, min_length=1, max_length=200)
    due_date: Optional[date] = None
    treatment_type: Optional[TreatmentType] = None
    status: Optional[TreatmentStatus] = None


class TreatmentActionResponse(TreatmentActionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
