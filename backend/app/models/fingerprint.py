"""
Fingerprint models for VeriClip AI media fingerprinting.
Spatiotemporal fingerprinting for robust media identification.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class FingerprintRequest(BaseModel):
    """Request to generate fingerprint for media."""
    media_asset_id: str = Field(min_length=3, description="ID of the media asset")
    media_url: str = Field(min_length=5, description="URL or path to media file")
    media_type: str = Field(description="Type: video, image, audio")
    metadata: Optional[dict] = Field(default=None, description="Optional metadata for fingerprinting")


class FingerprintResult(BaseModel):
    """Result of fingerprint generation."""
    model_config = {"protected_namespaces": ()}
    
    fingerprint_id: str
    media_asset_id: str
    fingerprint_hash: str = Field(min_length=64, max_length=64, description="SHA256 fingerprint hash")
    spatial_features: List[float] = Field(description="Spatial feature vector")
    temporal_features: List[float] = Field(description="Temporal feature vector")
    confidence: float = Field(ge=0.0, le=1.0, description="Fingerprint generation confidence")
    created_at: datetime
    model_version: str = Field(description="Model version used")


class FingerprintMatch(BaseModel):
    """Match result when comparing fingerprints."""
    match_id: str
    source_fingerprint_id: str
    target_fingerprint_id: str
    similarity_score: float = Field(ge=0.0, le=1.0, description="Similarity score between fingerprints")
    is_match: bool = Field(description="Whether this exceeds match threshold")
    match_threshold: float = Field(default=0.85, description="Threshold used for matching")
    matched_segments: Optional[List[dict]] = Field(default=None, description="Matched temporal segments for video")


class FingerprintList(BaseModel):
    """List of fingerprints."""
    items: List[FingerprintResult]
    total: int = Field(ge=0, description="Total count")
