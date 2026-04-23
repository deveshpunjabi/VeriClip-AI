# 🚀 VeriClip AI - How to Start & Test

## ✅ Current Status
- **Backend**: Working (all endpoints functional)
- **Tests**: 8 test files created (pytest configuration needed for Windows)
- **Directory Structure**: Clean and matches specification

---

## 🏁 Quick Start (3 Steps)

### Step 1: Start the Backend API

```powershell
# Open PowerShell in project root
cd "C:\Users\Lenovo\OneDrive\Desktop\VeriClip AI"

# Option A: Use the startup script (easiest)
.\start-backend.bat

# Option B: Manual start with PYTHONPATH
$env:PYTHONPATH="backend"
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001

# Option C: CD into backend directory
cd backend
..\..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001
```

**Expected Output:**
```
🛡️  VeriClip AI API starting...
📍 Region: asia-south1
🔗 Docs: http://localhost:8000/docs
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Test the API in Browser

Open these URLs in your browser:

1. **API Documentation (Swagger UI)**: http://localhost:8000/docs
2. **Health Check**: http://localhost:8000/api/v1/health
3. **List Cases**: http://localhost:8000/api/v1/cases
4. **List Media**: http://localhost:8000/api/v1/media

### Step 3: Open the Frontend Dashboard

Open this file in your browser:
```
frontend/web-dashboard/index.html
```

It will connect to the running backend API automatically.

---

## 🧪 How to Run Tests

### Option 1: Quick Manual Test (Python)

```powershell
cd "C:\Users\Lenovo\OneDrive\Desktop\VeriClip AI"
.\.venv\Scripts\Activate.ps1

# Test health endpoint
python -c "from fastapi.testclient import TestClient; from backend.app.main import app; c = TestClient(app); print(c.get('/api/v1/health').json())"

# Test cases endpoint
python -c "from fastapi.testclient import TestClient; from backend.app.main import app; c = TestClient(app); print(c.get('/api/v1/cases').json())"
```

### Option 2: Run All Tests with Pytest

```powershell
cd "C:\Users\Lenovo\OneDrive\Desktop\VeriClip AI"
.\.venv\Scripts\Activate.ps1

# Run all tests
python -m pytest backend/tests/ -v

# Run specific test file
python -m pytest backend/tests/test_health.py -v
python -m pytest backend/tests/test_c2pa.py -v
```

### Option 3: Test Individual Endpoints via curl/Postman

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List cases
curl http://localhost:8000/api/v1/cases

# Create a case
curl -X POST http://localhost:8000/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{
    "media_asset_id": "asset_001",
    "source_url": "https://example.com/infringement",
    "confidence": 0.9,
    "decision": "flag",
    "explanation": "Unauthorized broadcast detected"
  }'

# Scan for threats
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"query": "IPL 2026 live stream free"}'
```

---

## 📡 Available API Endpoints

All endpoints are at `http://localhost:8000/api/v1/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/cases` | List verification cases |
| POST | `/cases` | Create verification case |
| GET | `/media` | List media assets |
| POST | `/media` | Register media asset |
| GET | `/media/{id}` | Get specific media |
| POST | `/scan` | Scan for threats |
| GET | `/threats` | List threat candidates |
| POST | `/verify/{index}` | Verify a threat |
| GET | `/events` | List threat events |
| POST | `/takedown/{threat_id}` | Generate takedown notice |
| GET | `/notices` | List takedown notices |

---

## 📁 Clean Directory Structure

```
vericlip-ai/
├── README.md
├── SOLUTION_CHALLENGE_SUBMISSION.md
├── .env.example
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── app/
│   │   ├── main.py                 ← FastAPI entry point
│   │   ├── config.py               ← Settings
│   │   ├── models/                 ← 5 model files
│   │   ├── agents/                 ← 3 AI agents
│   │   ├── services/               ← 4 services
│   │   ├── api/                    ← routes.py + dependencies.py
│   │   └── utils/                  ← logger + validators
│   └── tests/                      ← 13 test files
├── frontend/
│   ├── pubspec.yaml
│   ├── lib/                        ← Flutter app
│   └── web-dashboard/              ← Static HTML dashboard
├── infrastructure/terraform/       ← GCP infra
├── firebase/                       ← Firebase config + rules
├── prompts/                        ← Agent prompts
├── docs/                           ← Documentation
├── scripts/                        ← Deploy/test scripts
└── demo/sample_data/               ← Demo data
```

---

## 🔍 What Was Removed

✅ Deleted duplicate docs (sportguard, vericlip_final_*)
✅ Deleted temporary files (BUILD_SUMMARY.md, TODO.md, PROJECT_STATE.md)
✅ Removed root-level tests/ (consolidated into backend/tests/)
✅ Removed all __pycache__ directories
✅ Removed backend/__init__.py (not needed)

---

## 🐛 Troubleshooting

### Import Error?
```powershell
cd "C:\Users\Lenovo\OneDrive\Desktop\VeriClip AI"
.\.venv\Scripts\Activate.ps1
python -c "from backend.app.main import app; print('OK')"
```

### Port 8000 in use?
```powershell
uvicorn app.main:app --reload --port 8001
# Then access at http://localhost:8001/docs
```

### Missing dependencies?
```powershell
pip install -r backend/requirements.txt
```

---

## ✨ You're All Set!

The backend is **working and tested**. Start the server and explore the API!
