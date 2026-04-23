"""
Case models for VeriClip AI verification workflow.
Tracks reviewable verification cases generated from verified threats.
"""

from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, HttpUrl

Decision = Literal["flag", "review", "ignore"]


class VerificationCaseCreate(BaseModel):
    """Request to create a new verification case."""
    media_asset_id: str = Field(min_length=3, description="ID of the media asset")
    source_url: HttpUrl = Field(description="URL where infringement was detected")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from verification")
    decision: Decision = Field(description="Verification decision: flag, review, or ignore")
    explanation: str = Field(min_length=10, description="Explanation for the decision")


class VerificationCase(VerificationCaseCreate):
    """A reviewable verification case generated from verified threats."""
    case_id: str
    created_at: datetime
    threat_id: Optional[str] = Field(default=None, description="Associated threat ID")
    assigned_to: Optional[str] = Field(default=None, description="Reviewer assignment")


class VerificationCaseList(BaseModel):
    """List of verification cases."""
    items: List[VerificationCase]
    total: int = Field(ge=0, description="Total count")
