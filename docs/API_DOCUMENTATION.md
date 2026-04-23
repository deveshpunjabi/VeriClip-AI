# VeriClip AI - API Documentation

## Base URL
```
Local:  http://localhost:8000/api/v1
Prod:   https://vericlip-api.run.app/api/v1
```

## Authentication
All endpoints require Firebase Auth token in `Authorization: Bearer <token>` header.

---

## Health & Status

### GET /health
Check API health.

**Response:**
```json
{
  "status": "ok",
  "service": "vericlip-api",
  "version": "0.1.0"
}
```

---

## Media Assets

### POST /media
Register a new media asset.

**Request Body:**
```json
{
  "title": "IPL 2026 Match 42",
  "original_url": "https://official-stream.com/ipl/match42.mp4",
  "file_size_bytes": 1073741824,
  "content_type": "video/mp4"
}
```

**Response (201 Created):**
```json
{
  "media_asset_id": "asset_a1b2c3d4e5",
  "title": "IPL 2026 Match 42",
  "original_url": "https://official-stream.com/ipl/match42.mp4",
  "file_size_bytes": 1073741824,
  "content_type": "video/mp4",
  "created_at": "2026-04-09T10:30:00Z",
  "fingerprint_hash": "e3b0c44298fc1c14..."
}
```

### GET /media/{media_asset_id}
Retrieve a media asset by ID.

**Response (200 OK):**
```json
{
  "media_asset_id": "asset_a1b2c3d4e5",
  "title": "IPL 2026 Match 42",
  "original_url": "https://official-stream.com/ipl/match42.mp4",
  "file_size_bytes": 1073741824,
  "content_type": "video/mp4",
  "created_at": "2026-04-09T10:30:00Z",
  "fingerprint_hash": "e3b0c44298fc1c14..."
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Media asset not found"
}
```

---

## Verification Cases

### GET /cases
List all verification cases.

**Response (200 OK):**
```json
{
  "items": [
    {
      "case_id": "case_seed_001",
      "media_asset_id": "asset_seed_001",
      "source_url": "https://example.com/seed-stream",
      "confidence": 0.76,
      "decision": "review",
      "explanation": "Seed case for dashboard initialization",
      "created_at": "2026-04-09T08:00:00Z"
    }
  ]
}
```

### POST /cases
Create a new verification case.

**Request Body:**
```json
{
  "media_asset_id": "asset_ipl_001",
  "source_url": "https://pirate-stream.com/live",
  "confidence": 0.82,
  "decision": "review",
  "explanation": "Temporal pattern and logo overlap detected"
}
```

**Response (201 Created):**
```json
{
  "case_id": "case_f7g8h9i0j1",
  "media_asset_id": "asset_ipl_001",
  "source_url": "https://pirate-stream.com/live",
  "confidence": 0.82,
  "decision": "review",
  "explanation": "Temporal pattern and logo overlap detected",
  "created_at": "2026-04-09T11:00:00Z"
}
```

---

## Fingerprinting

### POST /fingerprints/generate
Generate a fingerprint for a media asset.

**Request Body:**
```json
{
  "media_asset_id": "asset_a1b2c3d4e5",
  "media_url": "https://official-stream.com/ipl/match42.mp4",
  "media_type": "video",
  "metadata": {
    "event": "IPL 2026",
    "teams": ["MI", "CSK"]
  }
}
```

**Response (201 Created):**
```json
{
  "fingerprint_id": "fp_abc123def456",
  "media_asset_id": "asset_a1b2c3d4e5",
  "fingerprint_hash": "5d41402abc4b2a76b9719d911017c592...",
  "spatial_features": [0.123, 0.456, ...],
  "temporal_features": [0.789, 0.012, ...],
  "confidence": 0.94,
  "created_at": "2026-04-09T10:35:00Z",
  "model_version": "gemini-2.0-flash"
}
```

### POST /fingerprints/match
Compare two fingerprints for similarity.

**Request Body:**
```json
{
  "source_hash": "5d41402abc4b2a76b9719d911017c592...",
  "target_hash": "7d865e959b2466918c9863afca942d0f...",
  "source_features": [0.123, 0.456, ...],
  "target_features": [0.130, 0.460, ...]
}
```

**Response (200 OK):**
```json
{
  "match_id": "match_xyz789",
  "source_fingerprint_id": "5d41402abc4b2a76b9719d911017c592...",
  "target_fingerprint_id": "7d865e959b2466918c9863afca942d0f...",
  "similarity_score": 0.9234,
  "is_match": true,
  "match_threshold": 0.85
}
```

---

## Threats

### POST /threats/scan
Initiate a comprehensive scan across all sources.

**Request Body:**
```json
{
  "query": "IPL 2026 live stream free",
  "telegram_keywords": ["ipl free", "cricket live"],
  "source_fingerprint": "5d41402abc4b2a76b9719d911017c592..."
}
```

**Response (202 Accepted):**
```json
{
  "scan_id": "scan_abc123",
  "status": "queued",
  "estimated_completion": "2026-04-09T10:36:00Z"
}
```

### GET /threats
List all verified threats.

**Query Parameters:**
- `min_confidence`: Filter by minimum confidence (default: 0.0)
- `jurisdiction`: Filter by jurisdiction (IN, US, UK)
- `takedown_status`: Filter by status (pending, submitted, completed, rejected)

**Response (200 OK):**
```json
{
  "items": [
    {
      "threat_id": "threat_123abc",
      "media_asset_id": "asset_a1b2c3d4e5",
      "infringement_url": "https://pirate-site.com/ipl-stream",
      "infringement_title": "Watch IPL 2026 Live Free",
      "threat_level": "high",
      "confidence": 0.892,
      "evidence_urls": [],
      "fingerprint_match_score": 0.91,
      "takedown_status": "pending",
      "jurisdiction": "IN",
      "created_at": "2026-04-09T10:40:00Z",
      "verified_at": "2026-04-09T10:40:05Z"
    }
  ],
  "total": 1
}
```

---

## Takedown Notices

### POST /takedowns/generate
Generate a takedown notice for a verified threat.

**Request Body:**
```json
{
  "threat_id": "threat_123abc",
  "rights_holder": "BCCI",
  "rights_holder_email": "legal@bcci.tv"
}
```

**Response (201 Created):**
```json
{
  "notice_id": "notice_def456",
  "threat_id": "threat_123abc",
  "jurisdiction": "IN",
  "notice_type": "copyright_act_1957",
  "recipient": "pirate-site.com",
  "notice_content": "COPYRIGHT INFRINGEMENT NOTICE...",
  "status": "draft",
  "generated_at": "2026-04-09T10:41:00Z"
}
```

### POST /takedowns/{notice_id}/send
Send a generated takedown notice.

**Query Parameters:**
- `dry_run`: If true, log but don't actually send (default: true)

**Response (200 OK):**
```json
{
  "status": "dry_run",
  "notice_id": "notice_def456",
  "recipient": "pirate-site.com",
  "message": "Dry run: notice not actually sent"
}
```

---

## C2PA Provenance

### POST /c2pa/manifests
Generate a C2PA manifest for media segment.

**Request:** Multipart form with media file + metadata

**Response (201 Created):**
```json
{
  "stream_id": "550e8400-e29b-41d4-a716-446655440000",
  "sequence_number": 1,
  "assertion": {
    "assertion_type": "livevideo-segment-map",
    "stream_id": "550e8400-e29b-41d4-a716-446655440000",
    "sequence_number": 1,
    "segment_hash": "e3b0c44298fc1c14...",
    "timestamp": "2026-04-09T10:30:00Z"
  },
  "cose_signature": {
    "protected": {"1": -7},
    "payload": "...",
    "signature": "..."
  },
  "manifest_hash": "abc123..."
}
```

### POST /c2pa/validate
Validate a C2PA manifest chain.

**Request Body:**
```json
{
  "manifests": [...]
}
```

**Response (200 OK):**
```json
{
  "is_valid": true,
  "total_manifests": 10,
  "first_sequence": 1,
  "last_sequence": 10,
  "errors": [],
  "warnings": [],
  "validated_at": "2026-04-09T10:45:00Z"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `400`: Bad Request (validation failed)
- `401`: Unauthorized (missing/invalid auth)
- `404`: Not Found (resource doesn't exist)
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

---

## Rate Limits

- **Unauthenticated**: 10 requests/minute
- **Authenticated**: 100 requests/minute
- **Scan endpoints**: 5 requests/hour

Rate limit headers included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1649500800
```
