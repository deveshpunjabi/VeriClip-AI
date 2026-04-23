"""
C2PA Service for VeriClip AI.
Generates and validates cryptographic provenance chains for sports media.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4
import hashlib
import json
from app.config import settings
from app.models.c2pa_manifest import C2PAManifest, C2PAChainValidationResult
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class C2PAService:
    """Manages C2PA cryptographic provenance chains."""

    def __init__(self):
        self.algorithm = "ES256"
        self.key_id = settings.GOOGLE_CLOUD_PROJECT or "vericlip-dev"

    def generate_manifest(
        self,
        media_asset_id: str,
        sequence_number: int,
        title: str,
        prev_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> C2PAManifest:
        """Generate a C2PA manifest for a media segment."""
        assertion = {
            "label": "stds.schema-org.CreativeWork",
            "data": {
                "@context": "https://schema.org",
                "@type": "CreativeWork",
                "name": title,
                "identifier": media_asset_id,
                "position": sequence_number,
            },
        }
        if metadata:
            assertion["data"].update(metadata)

        payload = {
            "media_asset_id": media_asset_id,
            "sequence_number": sequence_number,
            "prev_hash": prev_hash,
            "assertion": assertion,
            "algorithm": self.algorithm,
            "key_id": self.key_id,
        }

        manifest_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        cose_signature = self._generate_cose_signature(manifest_hash)

        manifest = C2PAManifest(
            manifest_id=f"manifest_{uuid4().hex[:12]}",
            media_asset_id=media_asset_id,
            sequence_number=sequence_number,
            prev_hash=prev_hash,
            assertions=[assertion],
            cose_signature=cose_signature,
            manifest_hash=manifest_hash,
            created_at=datetime.now(timezone.utc),
        )

        logger.info(f"C2PA manifest generated: {manifest.manifest_id}, sequence={sequence_number}")
        return manifest

    def validate_chain(self, manifests: List[C2PAManifest]) -> C2PAChainValidationResult:
        """Validate a chain of C2PA manifests."""
        errors = []
        if not manifests:
            return C2PAChainValidationResult(is_valid=False, total_manifests=0, first_sequence=0, last_sequence=0, errors=["Empty chain"])

        sorted_manifests = sorted(manifests, key=lambda m: m.sequence_number)
        first_sequence = sorted_manifests[0].sequence_number
        last_sequence = sorted_manifests[-1].sequence_number

        for i, manifest in enumerate(sorted_manifests):
            if i > 0:
                expected_seq = sorted_manifests[i - 1].sequence_number + 1
                if manifest.sequence_number != expected_seq:
                    errors.append(f"Sequence gap: expected {expected_seq}, got {manifest.sequence_number}")
                prev_manifest = sorted_manifests[i - 1]
                if manifest.prev_hash != prev_manifest.manifest_hash:
                    errors.append(f"Hash break at sequence {manifest.sequence_number}")

            computed_hash = self._compute_expected_hash(manifest)
            if manifest.manifest_hash != computed_hash:
                errors.append(f"Manifest hash mismatch at sequence {manifest.sequence_number}")

        return C2PAChainValidationResult(
            is_valid=len(errors) == 0,
            total_manifests=len(sorted_manifests),
            first_sequence=first_sequence,
            last_sequence=last_sequence,
            errors=errors,
        )

    def validate_manifest_integrity(self, manifest: C2PAManifest, expected_hash: Optional[str] = None) -> C2PAChainValidationResult:
        """Validate a single manifest's integrity."""
        errors = []
        if expected_hash and manifest.manifest_hash != expected_hash:
            errors.append("Manifest has been tampered: hash mismatch")
        computed_hash = self._compute_expected_hash(manifest)
        if manifest.manifest_hash != computed_hash:
            errors.append("Manifest hash doesn't match computed hash")
        return C2PAChainValidationResult(is_valid=len(errors) == 0, total_manifests=1, first_sequence=manifest.sequence_number, last_sequence=manifest.sequence_number, errors=errors)

    def _generate_cose_signature(self, manifest_hash: str) -> Dict[str, str]:
        """Generate mock COSE_Sign1_Tagged signature."""
        return {"protected": "eyJhbGciOiJFUzI1NiJ9", "signature": hashlib.sha256(f"{manifest_hash}:{self.key_id}".encode()).hexdigest(), "key_id": self.key_id}

    def _compute_expected_hash(self, manifest: C2PAManifest) -> str:
        """Recompute the manifest hash from its content."""
        payload = {"media_asset_id": manifest.media_asset_id, "sequence_number": manifest.sequence_number, "prev_hash": manifest.prev_hash, "assertion": manifest.assertions[0] if manifest.assertions else {}, "algorithm": self.algorithm, "key_id": self.key_id}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
