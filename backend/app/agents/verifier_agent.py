"""
Verifier Agent for VeriClip AI.
Evaluates threat candidates using fingerprint matching, content analysis, and Gemini AI to produce verified threats with confidence scores.
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
from uuid import uuid4
import hashlib
from app.config import settings
from app.models.threat import ThreatCandidate, ThreatEvent
from app.services.gemini_service import GeminiService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VerifierAgent:
    """Verifies potential threats using AI-powered visual and contextual analysis."""

    def __init__(self):
        self.match_threshold = 0.85
        self.gemini_svc = GeminiService()

    async def verify_candidate(self, candidate: ThreatCandidate, original_fingerprint: Optional[str] = None, evidence_data: Optional[Dict] = None) -> ThreatEvent:
        """Verify a single threat candidate and produce a confirmed threat event."""
        logger.info(f"Verifying candidate: {candidate.url}")

        fingerprint_score = await self._calculate_fingerprint_match(candidate, original_fingerprint)
        contextual_score = await self._analyze_contextual_signals(candidate, evidence_data)
        
        # Use Gemini for deep verification if scores are high enough to be suspicious
        # but not conclusive (gray area)
        ai_verification_score = 0.0
        if 0.5 <= contextual_score <= 0.9:
            logger.info(f"Initiating Gemini deep verification for {candidate.url}")
            analysis = await self.gemini_svc.verify_infringement(
                original_media_desc=f"Official broadcast hash: {original_fingerprint}",
                suspected_media_desc=f"Title: {candidate.title}\nSnippet: {candidate.snippet}\nSource: {candidate.source}",
                evidence_context=str(evidence_data) if evidence_data else None
            )
            # Simple scoring from AI analysis text (in production, we'd parse JSON)
            if "infringe" in analysis.get("analysis", "").lower():
                ai_verification_score = 0.95
            else:
                ai_verification_score = 0.2

        # Combine scores
        if ai_verification_score > 0:
            combined_confidence = (fingerprint_score * 0.3) + (contextual_score * 0.2) + (ai_verification_score * 0.5)
        else:
            combined_confidence = (fingerprint_score * 0.6) + (contextual_score * 0.4)

        threat_level = self._classify_threat_level(combined_confidence)
        jurisdiction = self._detect_jurisdiction(candidate.url)

        return ThreatEvent(
            threat_id=f"threat_{uuid4().hex[:12]}",
            media_asset_id=candidate.source_fingerprint_hash or "unknown",
            infringement_url=candidate.url,
            infringement_title=candidate.title,
            threat_level=threat_level,
            confidence=round(combined_confidence, 3),
            evidence_urls=evidence_data.get("urls", []) if evidence_data else [],
            fingerprint_match_score=round(fingerprint_score, 3),
            takedown_status="pending",
            jurisdiction=jurisdiction,
            created_at=datetime.now(timezone.utc),
            verified_at=datetime.now(timezone.utc),
        )

    async def verify_batch(self, candidates: List[ThreatCandidate], original_fingerprint: Optional[str] = None, min_confidence: float = 0.7) -> List[ThreatEvent]:
        """Verify a batch of candidates and return only those meeting the confidence threshold."""
        logger.info(f"Verifying batch of {len(candidates)} candidates")
        verified_threats: List[ThreatEvent] = []
        for candidate in candidates:
            threat_event = await self.verify_candidate(candidate, original_fingerprint)
            if threat_event.confidence >= min_confidence:
                verified_threats.append(threat_event)
        logger.info(f"Batch verification complete: {len(verified_threats)}/{len(candidates)} verified")
        return verified_threats

    async def _calculate_fingerprint_match(self, candidate: ThreatCandidate, original_fingerprint: Optional[str] = None) -> float:
        """Calculate fingerprint similarity score."""
        if not original_fingerprint or not candidate.source_fingerprint_hash:
            return candidate.confidence
        if original_fingerprint == candidate.source_fingerprint_hash:
            return 0.98
        prefix_len = min(len(original_fingerprint), len(candidate.source_fingerprint_hash))
        matching_prefix = sum(1 for a, b in zip(original_fingerprint[:prefix_len], candidate.source_fingerprint_hash[:prefix_len]) if a == b)
        return matching_prefix / max(prefix_len, 1)

    async def _analyze_contextual_signals(self, candidate: ThreatCandidate, evidence_data: Optional[Dict] = None) -> float:
        """Analyze contextual signals to produce a confidence score."""
        score = 0.5
        source_scores = {"telegram": 0.7, "youtube": 0.6, "custom_search": 0.5, "twitter": 0.55, "facebook": 0.5}
        score = source_scores.get(candidate.source, 0.5)
        infringement_keywords = ["free stream", "live cricket", "ipl free", "watch online", "hd stream"]
        snippet_lower = candidate.snippet.lower()
        title_lower = candidate.title.lower()
        keyword_matches = sum(1 for kw in infringement_keywords if kw in snippet_lower or kw in title_lower)
        score += min(keyword_matches * 0.05, 0.2)
        if evidence_data:
            if evidence_data.get("has_screenshot"): score += 0.1
            if evidence_data.get("metadata_verified"): score += 0.15
        return min(score, 1.0)

    def _classify_threat_level(self, confidence: float) -> str:
        """Classify threat level based on confidence score."""
        if confidence >= 0.95: return "critical"
        elif confidence >= 0.85: return "high"
        elif confidence >= 0.7: return "medium"
        else: return "low"

    def _detect_jurisdiction(self, url: str) -> str:
        """Detect legal jurisdiction based on URL domain."""
        url_lower = url.lower()
        if any(x in url_lower for x in [".in", "t.me/ipl", "hotstar", "jeeotv"]): return "IN"
        if any(x in url_lower for x in [".com", "youtube.com", "facebook.com"]): return "US"
        if ".uk" in url_lower: return "UK"
        return "US"
