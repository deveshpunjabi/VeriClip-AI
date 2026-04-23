"""Unit tests for AI agents."""
import pytest
from app.agents.scanner_agent import ScannerAgent
from app.agents.verifier_agent import VerifierAgent
from app.agents.alert_agent import AlertAgent
from app.models.threat import ThreatCandidate, ThreatEvent


@pytest.mark.asyncio
async def test_scanner_scan_web():
    agent = ScannerAgent()
    candidates = await agent.scan_web("IPL 2026 live stream")
    assert isinstance(candidates, list)


@pytest.mark.asyncio
async def test_verifier_verify():
    agent = VerifierAgent()
    candidate = ThreatCandidate(
        url="https://example.com/stream",
        title="IPL Stream",
        snippet="Watch IPL cricket free",
        confidence=0.85,
        source="custom_search",
        source_fingerprint_hash="sha256:test_hash",
    )
    threat = await agent.verify_candidate(candidate)
    assert threat.threat_id.startswith("threat_")
    assert 0.0 <= threat.confidence <= 1.0


@pytest.mark.asyncio
async def test_alert_generate_notice():
    agent = AlertAgent()
    threat = ThreatEvent(
        threat_id="threat_test_001",
        media_asset_id="asset_001",
        infringement_url="https://youtube.com/watch?v=test",
        infringement_title="Unauthorized IPL Stream",
        threat_level="high",
        confidence=0.92,
        jurisdiction="US",
        fingerprint_match_score=0.88,
    )
    notice = await agent.generate_takedown_notice(threat)
    assert notice.notice_id.startswith("notice_")
    assert notice.jurisdiction == "US"
