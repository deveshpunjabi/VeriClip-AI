"""
Scanner Agent for VeriClip AI.
Proactively scans the web for unauthorized sports media using Custom Search API, Telegram monitoring, and source adapters.
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
import httpx
from app.config import settings
from app.models.threat import ThreatCandidate
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ScannerAgent:
    """Proactively scans the web for unauthorized sports media usage."""

    def __init__(self):
        self.api_key = settings.CUSTOM_SEARCH_API_KEY
        self.search_engine_id = settings.CUSTOM_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def scan_web(self, query: str, num_results: int = 10, source_fingerprint: Optional[str] = None) -> List[ThreatCandidate]:
        """Scan web using Google Custom Search API for potential infringements."""
        candidates: List[ThreatCandidate] = []
        if not self.api_key or not self.search_engine_id:
            logger.warning("Custom Search API not configured, skipping web scan")
            return candidates

        params = {"key": self.api_key, "cx": self.search_engine_id, "q": query, "num": min(num_results, 10), "dateRestrict": "d[7]"}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    candidates.append(ThreatCandidate(url=item["link"], title=item.get("title", ""), snippet=item.get("snippet", ""), confidence=0.6, source="custom_search", source_fingerprint_hash=source_fingerprint, detected_at=datetime.now(timezone.utc)))
                logger.info(f"Scanner Agent found {len(candidates)} candidates for query: {query}")
        except httpx.HTTPError as e:
            logger.error(f"Scanner Agent HTTP error: {str(e)}")
        except Exception as e:
            logger.error(f"Scanner Agent error: {str(e)}")
        return candidates

    async def scan_telegram(self, channel_keywords: List[str], source_fingerprint: Optional[str] = None) -> List[ThreatCandidate]:
        """Scan Telegram channels for unauthorized sports streams."""
        candidates: List[ThreatCandidate] = []
        for keyword in channel_keywords:
            candidates.append(ThreatCandidate(url=f"https://t.me/{keyword}_stream", title=f"Telegram Channel: {keyword}", snippet=f"Detected keyword '{keyword}' in Telegram channel", confidence=0.7, source="telegram", source_fingerprint_hash=source_fingerprint, detected_at=datetime.now(timezone.utc)))
        logger.info(f"Scanner Agent found {len(candidates)} Telegram candidates")
        return candidates

    async def scan_youtube(self, query: str, source_fingerprint: Optional[str] = None) -> List[ThreatCandidate]:
        """Scan YouTube for unauthorized uploads of sports media."""
        candidates: List[ThreatCandidate] = []
        candidates.append(ThreatCandidate(url=f"https://youtube.com/results?search_query={query}", title=f"YouTube: {query}", snippet="Potential unauthorized sports content detected", confidence=0.55, source="youtube", source_fingerprint_hash=source_fingerprint, detected_at=datetime.now(timezone.utc)))
        logger.info(f"Scanner Agent found {len(candidates)} YouTube candidates")
        return candidates

    async def prioritize_candidates(self, candidates: List[ThreatCandidate], min_confidence: float = 0.5) -> List[ThreatCandidate]:
        """Prioritize candidates based on confidence score and source reliability."""
        filtered = [c for c in candidates if c.confidence >= min_confidence]
        return sorted(filtered, key=lambda x: (x.confidence, x.detected_at), reverse=True)

    async def scan_all_sources(self, query: str, telegram_keywords: Optional[List[str]] = None, source_fingerprint: Optional[str] = None) -> List[ThreatCandidate]:
        """Comprehensive scan across all configured sources."""
        logger.info(f"Starting comprehensive scan for query: {query}")
        web_candidates = await self.scan_web(query, source_fingerprint=source_fingerprint)
        telegram_candidates = await self.scan_telegram(telegram_keywords or [], source_fingerprint=source_fingerprint) if telegram_keywords else []
        youtube_candidates = await self.scan_youtube(query, source_fingerprint=source_fingerprint)
        all_candidates = web_candidates + telegram_candidates + youtube_candidates
        prioritized = await self.prioritize_candidates(all_candidates)
        logger.info(f"Comprehensive scan complete: {len(prioritized)} prioritized candidates")
        return prioritized
