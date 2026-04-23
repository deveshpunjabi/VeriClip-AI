"""
VeriClip AI API - Unified Routes
All API endpoints in a single file for streamlined deployment.
"""

import json
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field

# Models
from app.models.case import VerificationCase, VerificationCaseCreate, VerificationCaseList
from app.models.media import MediaAsset, MediaAssetCreate, MediaAssetList
from app.models.threat import ThreatCandidate, ThreatCandidateList, ThreatEvent, ThreatEventList, TakedownNotice
from app.models.fingerprint import FingerprintRequest, FingerprintResult

# Agents
from app.agents.scanner_agent import ScannerAgent
from app.agents.verifier_agent import VerifierAgent
from app.agents.alert_agent import AlertAgent

# Services
from app.services.fingerprint_service import FingerprintService
from app.services.c2pa_service import C2PAService
from app.services.gemini_service import GeminiService

logger = __import__('logging').getLogger(__name__)

router = APIRouter()

# Initialize Firebase Admin
class MockFirestore:
    """Mock Firestore client for local development and tests."""
    def __init__(self):
        self._data = {}  # {collection_name: {doc_id: data}}

    def collection(self, name):
        if name not in self._data:
            self._data[name] = {}
        self._current_col = name
        return self

    def document(self, id):
        self._current_doc_id = id
        return self

    def set(self, data):
        self._data[self._current_col][self._current_doc_id] = data

    def get(self):
        class Doc:
            def __init__(self, exists, data):
                self.exists = exists
                self._data = data
            def to_dict(self): return self._data
        
        col_data = self._data.get(self._current_col, {})
        doc_data = col_data.get(self._current_doc_id)
        return Doc(doc_data is not None, doc_data or {})

    def stream(self):
        class Doc:
            def __init__(self, data): self._data = data
            def to_dict(self): return self._data
        
        return [Doc(d) for d in self._data.get(self._current_col, {}).values()]

    def add(self, data):
        doc_id = uuid4().hex
        self._data[self._current_col][doc_id] = data
        return None, None

    def where(self, *args): return self
    def order_by(self, *args): return self

if not firebase_admin._apps:
    try:
        firebase_admin.initialize_app()
        db = firestore.client()
    except Exception as e:
        logger.warning(f"Firebase initialization failed, using MockFirestore: {e}")
        db = MockFirestore()
else:
    try:
        db = firestore.client()
    except Exception as e:
        logger.warning(f"Firestore client initialization failed, using MockFirestore: {e}")
        db = MockFirestore()

# Add rich seed data if using MockFirestore for judging/demo purposes
if isinstance(db, MockFirestore):
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # 1. Seed Media Assets (Official Broadcasts)
    db.collection("media").document("asset_ipl_001").set({
        "media_asset_id": "asset_ipl_001",
        "title": "IPL 2026 Final - Official Broadcast",
        "original_url": "https://official-sports.com/ipl-2026-final",
        "content_type": "video/mp4",
        "rights_holder": "BCCI",
        "event_tags": ["IPL", "2026", "Final", "Cricket"],
        "created_at": now_iso,
        "fingerprint_hash": "a8f39c2...b9c1",
        "c2pa_manifest_id": "c2pa_bcci_xyz",
        "file_size_bytes": 1024000
    })

    # 2. Seed Threat Candidates (From Scanner Agent)
    db.collection("candidates").add({
        "url": "https://t.me/ipl_free_streams_2026",
        "title": "[LIVE] IPL 2026 FINAL FREE HD",
        "snippet": "Watch the IPL final free without subscription. Join now!",
        "confidence": 0.85,
        "source": "telegram",
        "detected_at": now_iso,
        "source_fingerprint_hash": "a8f39c2...b9c1"
    })
    db.collection("candidates").add({
        "url": "https://youtube.com/watch?v=illegal123",
        "title": "CSK vs MI Live Match Free",
        "snippet": "Live stream of the match. Subscribe for more.",
        "confidence": 0.92,
        "source": "youtube",
        "detected_at": now_iso,
        "source_fingerprint_hash": "a8f39c2...b9c1"
    })

    # 3. Seed Confirmed Threat Events (Verified by Gemini)
    db.collection("events").document("threat_evt_001").set({
        "threat_id": "threat_evt_001",
        "media_asset_id": "asset_ipl_001",
        "infringement_url": "https://twitch.tv/fake_sports_channel",
        "infringement_title": "IPL Final Watch Party (Restream)",
        "threat_level": "critical",
        "confidence": 0.98,
        "evidence_urls": ["https://storage.googleapis.com/vericlip/evidence_1.png"],
        "fingerprint_match_score": 0.94,
        "takedown_status": "submitted",
        "jurisdiction": "IN",
        "recipient": "Twitch Interactive, Inc.",
        "created_at": now_iso,
        "verified_at": now_iso
    })

    # 4. Seed Takedown Notices (Generated by Alert Agent)
    db.collection("notices").document("notice_001").set({
        "notice_id": "notice_001",
        "threat_id": "threat_evt_001",
        "jurisdiction": "IN",
        "notice_type": "copyright_act_1957",
        "recipient": "Twitch Legal Dept",
        "notice_content": "LEGAL DEMAND FOR CONTENT REMOVAL\n\nUnder Section 52 of the Indian Copyright Act 1957, we demand immediate removal of the infringing broadcast of the 'IPL 2026 Final' located at https://twitch.tv/fake_sports_channel.\n\nOur spatiotemporal AI engine has matched the live stream fingerprint against the original BCCI broadcast with 94.2% accuracy. This constitutes unauthorized distribution of digital intellectual property.\n\nFailure to remove the content within 24 hours will result in legal action.",
        "status": "sent",
        "generated_at": now_iso,
        "sent_at": now_iso
    })

# Initialize agents and services
scanner = ScannerAgent()
verifier = VerifierAgent()
alerter = AlertAgent()
fingerprint_svc = FingerprintService()
c2pa_svc = C2PAService()
gemini_svc = GeminiService()


# ==================== HEALTH ====================

@router.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.2.0", "timestamp": datetime.now(timezone.utc).isoformat()}


# ==================== CASES ====================

@router.get("/cases", response_model=VerificationCaseList, tags=["cases"])
def list_cases():
    """List all verification cases."""
    docs = db.collection("cases").stream()
    items = [VerificationCase(**doc.to_dict()) for doc in docs]
    return VerificationCaseList(items=items, total=len(items))


@router.post("/cases", response_model=VerificationCase, status_code=status.HTTP_201_CREATED, tags=["cases"])
def create_case(payload: VerificationCaseCreate):
    """Create a new verification case."""
    item = VerificationCase(case_id=f"case_{uuid4().hex[:10]}", created_at=datetime.now(timezone.utc), **payload.model_dump())
    db.collection("cases").document(item.case_id).set(item.model_dump())
    return item


# ==================== MEDIA ====================

@router.post("/media", response_model=MediaAsset, status_code=status.HTTP_201_CREATED, tags=["media"])
def create_media(payload: MediaAssetCreate):
    """Register a new media asset."""
    item = MediaAsset(media_asset_id=f"asset_{uuid4().hex[:10]}", created_at=datetime.now(timezone.utc), fingerprint_hash=None, **payload.model_dump())
    db.collection("media").document(item.media_asset_id).set(item.model_dump())
    return item


@router.get("/media", response_model=MediaAssetList, tags=["media"])
def list_media():
    """List all registered media assets."""
    docs = db.collection("media").stream()
    items = [MediaAsset(**doc.to_dict()) for doc in docs]
    return MediaAssetList(items=items, total=len(items))


@router.get("/media/{media_asset_id}", response_model=MediaAsset, tags=["media"])
def get_media(media_asset_id: str):
    """Get a specific media asset by ID."""
    doc = db.collection("media").document(media_asset_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return MediaAsset(**doc.to_dict())


# ==================== THREATS / SCANNING ====================

class ScanRequest(BaseModel):
    """Request body for scan endpoint."""
    query: str = Field(min_length=3, description="Search query for infringement detection")
    media_asset_id: Optional[str] = None
    fingerprint_hash: Optional[str] = None
    telegram_keywords: Optional[List[str]] = None


@router.post("/scan", response_model=ThreatCandidateList, status_code=status.HTTP_201_CREATED, tags=["threats"])
async def scan_for_threats(request: ScanRequest):
    """Initiate a scan across web, Telegram, and YouTube for potential infringements."""
    candidates = await scanner.scan_all_sources(
        query=request.query,
        telegram_keywords=request.telegram_keywords,
        source_fingerprint=request.fingerprint_hash,
    )
    # Save to Firestore
    for candidate in candidates:
        # Use a hash of URL as ID to avoid duplicates if needed, or just auto-id
        db.collection("candidates").add(candidate.model_dump())
    return ThreatCandidateList(items=candidates, total=len(candidates))


@router.get("/threats", response_model=ThreatCandidateList, tags=["threats"])
def list_threats(min_confidence: float = 0.0):
    """List all discovered threat candidates."""
    docs = db.collection("candidates").where("confidence", ">=", min_confidence).stream()
    items = [ThreatCandidate(**doc.to_dict()) for doc in docs]
    return ThreatCandidateList(items=items, total=len(items))


# ==================== VERIFICATION ====================

@router.post("/verify/{candidate_index}", response_model=ThreatEvent, status_code=status.HTTP_201_CREATED, tags=["verification"])
async def verify_threat(candidate_index: int, media_asset_id: Optional[str] = None):
    """Verify a specific candidate and promote it to a confirmed threat event."""
    # To maintain the index-based API, we must fetch and sort
    docs = list(db.collection("candidates").order_by("detected_at").stream())
    if candidate_index < 0 or candidate_index >= len(docs):
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate_doc = docs[candidate_index]
    candidate = ThreatCandidate(**candidate_doc.to_dict())
    
    threat_event = await verifier.verify_candidate(candidate=candidate, original_fingerprint=media_asset_id)
    
    # Save event and optionally remove candidate
    db.collection("events").document(threat_event.threat_id).set(threat_event.model_dump())
    # candidate_doc.reference.delete() # Optional: remove from candidates once verified
    
    return threat_event


@router.post("/verify-batch", response_model=ThreatEventList, status_code=status.HTTP_201_CREATED, tags=["verification"])
async def verify_batch_threats(min_confidence: float = 0.7):
    """Verify all pending candidates above minimum confidence threshold."""
    docs = db.collection("candidates").where("confidence", ">=", min_confidence).stream()
    candidates = [ThreatCandidate(**doc.to_dict()) for doc in docs]
    
    verified = await verifier.verify_batch(candidates=candidates, min_confidence=min_confidence)
    
    # Save to Firestore
    for event in verified:
        db.collection("events").document(event.threat_id).set(event.model_dump())

    return ThreatEventList(items=verified, total=len(verified))


@router.get("/events", response_model=ThreatEventList, tags=["verification"])
def list_events(threat_level: Optional[str] = None):
    """List all confirmed threat events."""
    query = db.collection("events")
    if threat_level:
        query = query.where("threat_level", "==", threat_level)
    
    docs = query.stream()
    items = [ThreatEvent(**doc.to_dict()) for doc in docs]
    return ThreatEventList(items=items, total=len(items))


# ==================== TAKEDOWN NOTICES ====================

@router.post("/takedown/{threat_id}", response_model=TakedownNotice, status_code=status.HTTP_201_CREATED, tags=["takedowns"])
async def generate_takedown(threat_id: str, dry_run: bool = True):
    """Generate a jurisdiction-compliant takedown notice for a confirmed threat."""
    doc = db.collection("events").document(threat_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Threat event not found")
    
    threat = ThreatEvent(**doc.to_dict())
    notice = await alerter.generate_takedown_notice(threat=threat)
    
    if not dry_run:
        await alerter.send_notice(notice, dry_run=False)
        notice.status = "sent"
        notice.sent_at = datetime.now(timezone.utc)
    
    db.collection("notices").document(notice.notice_id).set(notice.model_dump())
    return notice


@router.get("/notices", response_model=List[TakedownNotice], tags=["takedowns"])
def list_notices(status_filter: Optional[str] = None):
    """List all generated takedown notices."""
    query = db.collection("notices")
    if status_filter:
        query = query.where("status", "==", status_filter)
    
    docs = query.stream()
    return [TakedownNotice(**doc.to_dict()) for doc in docs]


# ==================== FINGERPRINT ====================

@router.post("/fingerprint", response_model=FingerprintResult, status_code=status.HTTP_201_CREATED, tags=["fingerprint"])
async def generate_fingerprint(request: FingerprintRequest):
    """Generate a spatiotemporal fingerprint for a media asset."""
    return await fingerprint_svc.generate_fingerprint(request)
