"""
C2PA manifest models for VeriClip AI.
Cryptographic provenance chain for sports media tracking.
Implements C2PA 2.4 spec with livevideo-segment-map assertion.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class C2PAManifest(BaseModel):
    """
    C2PA cryptographic manifest for a media segment.
    Provides tamper-evident chain of custody for sports media.
    """
    manifest_id: str = Field(default="", description="Unique identifier for this manifest")
    media_asset_id: str = Field(default="", description="ID of the media asset")
    sequence_number: int = Field(default=1, ge=1, description="Sequential number in the chain")
    prev_hash: Optional[str] = Field(default=None, description="Hash of previous manifest in chain")
    assertions: List[Dict[str, Any]] = Field(default_factory=list, description="C2PA assertion payloads")
    cose_signature: Dict[str, str] = Field(default_factory=dict, description="COSE_Sign1_Tagged signature structure")
    manifest_hash: str = Field(default="", min_length=64, max_length=64, description="SHA256 hash of the manifest")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class C2PAChainValidationResult(BaseModel):
    """Result of validating a C2PA manifest chain."""
    is_valid: bool = Field(description="Whether the chain is intact")
    total_manifests: int = Field(ge=0, description="Number of manifests validated")
    first_sequence: int
    last_sequence: int
    errors: List[str] = Field(default_factory=list, description="Validation errors found")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings during validation")
    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class C2PAPublicKey(BaseModel):
    """Public key for third-party C2PA verification."""
    key_id: str
    public_key_pem: str = Field(description="PEM-encoded public key")
    algorithm: str = Field(default="ES256", description="Signing algorithm")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(default=None, description="Key expiration (None = no expiry)")
