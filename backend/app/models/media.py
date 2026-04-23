"""
Media asset models for VeriClip AI.
Tracks official sports media assets for fingerprinting and comparison.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class MediaAssetCreate(BaseModel):
    """Request to register a new media asset."""
    title: str = Field(min_length=1, max_length=200, description="Human-readable title or name")
    original_url: HttpUrl = Field(description="Source URL of the original media")
    file_size_bytes: Optional[int] = Field(default=None, ge=0, description="Optional file size in bytes")
    content_type: str = Field(min_length=3, description="MIME type, e.g., video/mp4")
    rights_holder: Optional[str] = Field(default=None, description="Entity holding rights")
    event_tags: list[str] = Field(default_factory=list, description="Sports event tags (e.g., IPL, 2026)")


class MediaAsset(MediaAssetCreate):
    """Registered media asset with fingerprint metadata."""
    media_asset_id: str
    created_at: datetime
    fingerprint_hash: Optional[str] = Field(None, description="SHA256 hash or media fingerprint (populated later)")
    c2pa_manifest_id: Optional[str] = Field(None, description="Associated C2PA manifest ID")


class MediaAssetList(BaseModel):
    """List of media assets."""
    items: list[MediaAsset]
    total: int = Field(ge=0, description="Total count")
