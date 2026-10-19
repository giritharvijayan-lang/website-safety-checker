from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class CategoryName(str, Enum):
    PHISHING = "phishing"
    MALWARE = "malware"
    SHOPPING_TRUST = "shopping_trust"
    SCAM_OFFER = "scam_offer"
    CONNECTION_SECURITY = "connection_security"
    TRACKERS = "trackers"
    REPUTATION = "reputation"


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"
    NOT_ENOUGH_INFO = "NOT_ENOUGH_INFO"


class OverallVerdict(str, Enum):
    LOOKS_OK = "LOOKS_OK"
    SUSPICIOUS = "SUSPICIOUS"
    DANGEROUS = "DANGEROUS"
    NOT_ENOUGH_INFO = "NOT_ENOUGH_INFO"


class Signal(BaseModel):
    name: str
    description: str
    severity: str = "INFO"
    details: Optional[dict[str, Any]] = None


class CategoryResult(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    risk_level: str
    signals: list[Signal] = Field(default_factory=list)
    details: Optional[dict[str, Any]] = None


class OverallResult(BaseModel):
    score: int = Field(ge=0, le=100)
    verdict: str
    label: str
    summary: Optional[str] = None
    max_risk_category: Optional[str] = None


class ScanRequest(BaseModel):
    url: str
    site_type: Optional[str] = "general"


class ScanResponse(BaseModel):
    scan_id: str
    url: str
    domain: str
    site_type: str
    overall: OverallResult
    categories: list[CategoryResult]
