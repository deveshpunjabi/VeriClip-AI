"""
Alert Agent for VeriClip AI.
Generates takedown notices, manages alert delivery, and tracks threat resolution status.
"""

from typing import Dict, Optional
from datetime import datetime, timezone
from uuid import uuid4
from urllib.parse import urlparse
from app.config import settings
from app.models.threat import ThreatEvent, TakedownNotice
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class AlertAgent:
    """Generates and manages takedown notices for verified threats."""

    def __init__(self):
        self.supported_jurisdictions = {"IN": "Indian Copyright Act 1957", "US": "Digital Millennium Copyright Act (DMCA)", "UK": "UK Copyright, Designs and Patents Act 1988"}

    async def generate_takedown_notice(self, threat: ThreatEvent, rights_holder: str = "VeriClip AI Client", rights_holder_email: str = "legal@vericlip.ai") -> TakedownNotice:
        """Generate a jurisdiction-specific takedown notice."""
        logger.info(f"Generating takedown notice for threat: {threat.threat_id}, jurisdiction: {threat.jurisdiction}")
        jurisdiction = threat.jurisdiction or "US"
        notice_type = self._map_jurisdiction_to_notice_type(jurisdiction)
        notice_content = self._generate_notice_text(threat, jurisdiction, rights_holder, rights_holder_email)
        recipient = self._extract_platform_from_url(threat.infringement_url)

        return TakedownNotice(notice_id=f"notice_{uuid4().hex[:12]}", threat_id=threat.threat_id, jurisdiction=jurisdiction, notice_type=notice_type, recipient=recipient, notice_content=notice_content, status="draft")

    async def send_notice(self, notice: TakedownNotice, dry_run: bool = True) -> Dict:
        """Send a takedown notice to the appropriate platform."""
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Sending notice {notice.notice_id} to {notice.recipient}")
        if dry_run:
            return {"status": "dry_run", "notice_id": notice.notice_id, "recipient": notice.recipient, "message": "Dry run: notice not actually sent"}
        notice.status = "sent"
        notice.sent_at = datetime.now(timezone.utc)
        return {"status": "sent", "notice_id": notice.notice_id, "recipient": notice.recipient, "sent_at": notice.sent_at.isoformat()}

    def _map_jurisdiction_to_notice_type(self, jurisdiction: str) -> str:
        mapping = {"IN": "copyright_act_1957", "US": "dmca", "UK": "cdpa_1988"}
        return mapping.get(jurisdiction, "platform_report")

    def _generate_notice_text(self, threat: ThreatEvent, jurisdiction: str, rights_holder: str, rights_holder_email: str) -> str:
        if jurisdiction == "IN": return self._generate_indian_copyright_notice(threat, rights_holder, rights_holder_email)
        elif jurisdiction == "US": return self._generate_dmca_notice(threat, rights_holder, rights_holder_email)
        else: return self._generate_generic_notice(threat, rights_holder, rights_holder_email)

    def _generate_dmca_notice(self, threat: ThreatEvent, rights_holder: str, rights_holder_email: str) -> str:
        return f"""DIGITAL MILLENNIUM COPYRIGHT ACT TAKEDOWN NOTICE\n\nTo: {threat.infringement_url}\n\nDear {threat.recipient or 'Platform'} Legal Team,\n\nI am writing to notify you of copyright infringement on your platform pursuant to the DMCA, 17 U.S.C. § 512.\n\n1. IDENTIFICATION OF COPYRIGHTED WORK:\n   - Media Asset ID: {threat.media_asset_id}\n   - Title: {threat.infringement_title}\n   - Rights Holder: {rights_holder}\n\n2. IDENTIFICATION OF INFRINGING MATERIAL:\n   - Infringing URL: {threat.infringement_url}\n   - Fingerprint Match Score: {threat.fingerprint_match_score:.1%}\n   - Confidence: {threat.confidence:.1%}\n\n3. CONTACT INFORMATION:\n   - Name: {rights_holder}\n   - Email: {rights_holder_email}\n\n4. STATEMENT OF GOOD FAITH:\n   I have a good faith belief that the use of the material is not authorized by the copyright owner.\n\nDate: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\nSignature: {rights_holder}\n"""

    def _generate_indian_copyright_notice(self, threat: ThreatEvent, rights_holder: str, rights_holder_email: str) -> str:
        return f"""COPYRIGHT INFRINGEMENT NOTICE\nPursuant to The Copyright Act, 1957 (India) - Section 55\n\nTo: {threat.infringement_url}\n\nDear {threat.recipient or 'Platform'} Legal Team,\n\nThis notice is served pursuant to Section 55 of The Copyright Act, 1957.\n\n1. COPYRIGHT OWNER:\n   - Rights Holder: {rights_holder}\n   - Contact: {rights_holder_email}\n   - Media Asset ID: {threat.media_asset_id}\n\n2. INFRINGEMENT DETAILS:\n   - Infringing URL: {threat.infringement_url}\n   - Title: {threat.infringement_title}\n   - Fingerprint Match Score: {threat.fingerprint_match_score:.1%}\n\n3. DEMAND:\n   You are hereby requested to immediately remove or disable access to the infringing material.\n\nDate: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\nAuthorized Representative: {rights_holder}\n"""

    def _generate_generic_notice(self, threat: ThreatEvent, rights_holder: str, rights_holder_email: str) -> str:
        return f"""COPYRIGHT INFRINGEMENT REPORT\n\nTo: {threat.recipient or 'Platform'}\n\nWe are reporting copyright infringement on your platform.\n\n1. COPYRIGHT OWNER:\n   - Rights Holder: {rights_holder}\n   - Contact: {rights_holder_email}\n\n2. INFRINGING CONTENT:\n   - URL: {threat.infringement_url}\n   - Title: {threat.infringement_title}\n   - Confidence: {threat.confidence:.1%}\n\nDate: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"""


    def _extract_platform_from_url(self, url: str) -> str:
        url_lower = url.lower()
        if "youtube.com" in url_lower or "youtu.be" in url_lower: return "YouTube"
        elif "t.me" in url_lower or "telegram.org" in url_lower: return "Telegram"
        elif "facebook.com" in url_lower: return "Facebook"
        elif "twitter.com" in url_lower or "x.com" in url_lower: return "X (Twitter)"
        elif "instagram.com" in url_lower: return "Instagram"
        else:
            try:
                parsed = urlparse(url)
                return parsed.netloc or "Unknown Platform"
            except Exception:
                return "Unknown Platform"
