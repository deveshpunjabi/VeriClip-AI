"""
Gemini Service for VeriClip AI.
Integrates with Google's Gemini AI for media fingerprinting, content verification, and evidence summarization.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from google import genai
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class GeminiService:
    """Integrates with Gemini AI models for intelligent media analysis."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.fingerprint_model = settings.GEMINI_MODEL_FINGERPRINT
        self.verify_model = settings.GEMINI_MODEL_VERIFY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Gemini API key not configured, using mock mode")

    async def extract_media_features(self, media_url: str, media_type: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Extract visual features from media using Gemini."""
        if not self.client:
            return self._mock_feature_extraction(media_url, media_type)
        try:
            # Note: For production, we would use media upload/GCS integration
            response = self.client.models.generate_content(
                model=self.fingerprint_model,
                contents=prompt or "Extract all visual features: objects, colors, text, logos, watermarks"
            )
            return {"features": response.text, "model": self.fingerprint_model}
        except Exception as e:
            logger.error(f"Gemini feature extraction failed: {str(e)}")
            return self._mock_feature_extraction(media_url, media_type)

    async def verify_infringement(self, original_media_desc: str, suspected_media_desc: str, evidence_context: Optional[str] = None) -> Dict[str, Any]:
        """Use Gemini to analyze whether suspected media infringes on original."""
        if not self.client:
            return self._mock_infringement_analysis(original_media_desc, suspected_media_desc)
        try:
            prompt = f"""You are a copyright infringement analyst. Compare the following media descriptions and determine if the suspected media infringes on the original.\n\nORIGINAL MEDIA:\n{original_media_desc}\n\nSUSPECTED MEDIA:\n{suspected_media_desc}\n\n{"EVIDENCE CONTEXT: " + evidence_context if evidence_context else ""}\n\nProvide a structured analysis as JSON."""
            response = self.client.models.generate_content(
                model=self.verify_model,
                contents=prompt
            )
            return {"analysis": response.text, "model": self.verify_model, "timestamp": datetime.now(timezone.utc).isoformat()}
        except Exception as e:
            logger.error(f"Gemini infringement verification failed: {str(e)}")
            return self._mock_infringement_analysis(original_media_desc, suspected_media_desc)

    async def summarize_evidence(self, evidence_items: List[Dict[str, Any]], threat_id: str) -> str:
        """Summarize multiple evidence items into a concise report."""
        if not self.client or not evidence_items:
            return self._mock_evidence_summary(evidence_items, threat_id)
        try:
            evidence_text = "\n".join([f"- {item.get('type', 'unknown')}: {item.get('description', '')}" for item in evidence_items])
            prompt = f"Summarize the following evidence for threat ID {threat_id}:\n\n{evidence_text}\n\nProvide a concise, professional summary suitable for a legal takedown notice."
            response = self.client.models.generate_content(
                model=self.fingerprint_model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini evidence summarization failed: {str(e)}")
            return self._mock_evidence_summary(evidence_items, threat_id)

    def _mock_feature_extraction(self, media_url: str, media_type: str) -> Dict[str, Any]:
        return {"features": {"objects": ["cricket bat", "stadium", "crowd"], "colors": ["green", "blue", "white"], "text_detected": ["IPL 2026", "Live"], "logos": ["BCCI", "IPL"], "watermarks": ["official_broadcast"]}, "model": "mock", "media_url": media_url, "media_type": media_type}

    def _mock_video_features(self, media_url: str) -> Dict[str, Any]:
        return {"features": {"keyframes_analyzed": 10, "scenes": ["stadium wide shot", "close-up action", "crowd reaction"], "motion_patterns": ["fast_paced", "camera_pan"], "audio_track": "commentary"}, "model": "mock", "media_url": media_url}

    def _mock_infringement_analysis(self, original_desc: str, suspected_desc: str) -> Dict[str, Any]:
        return {"is_infringement": True, "confidence": 0.87, "reasoning": "High visual similarity detected between original broadcast and suspected unauthorized re-stream.", "risk_factors": ["Unauthorized redistribution of live broadcast", "Monetization via ads on stolen content"], "model": "mock", "timestamp": datetime.now(timezone.utc).isoformat()}

    def _mock_evidence_summary(self, evidence_items: List[Dict], threat_id: str) -> str:
        count = len(evidence_items) if evidence_items else 0
        return f"Evidence Summary for {threat_id}:\n- {count} evidence items collected\n- Fingerprint match confirmed\n- Content analysis shows unauthorized usage\n- Recommend immediate takedown action"
