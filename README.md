# TrustLens — Financial Content Verification Assistant

> **Understand before you trust.**  
> *AI-powered financial content risk-awareness assistant for first-time investors.*

---

## 1. Project Purpose & Problem Statement

In the digital era, retail and first-time investors are inundated with unsolicited investment tips, guaranteed return claims, and dubious advisory channels across WhatsApp, Telegram, Instagram, and SMS. Many cannot discern legitimate regulatory-compliant offerings from predatory schemes.

**TrustLens** is built for financial awareness hackathons to bridge this knowledge gap. It provides:
* **Objective risk assessment:** Categorizes content into **`LOW RISK`**, **`NEEDS VERIFICATION`**, or **`HIGH RISK`**.
* **Prototype Heuristic Score (0–100):** Clear indicator based on detected manipulation patterns (not a fraud probability).
* **Transparent Red Flags:** Pinpoints urgency, guaranteed returns, credential requests, and upfront payment demands.
* **Itemized Claim Verification:** Cross-checks specific claims against official regulatory frameworks (SEBI, RBI, NPCI).
* **Sequential Timeline:** Explains step-by-step why specific flags were raised.
* **Actionable Guidance:** Provides explicit **DO** and **DON'T** safety steps.

> **CRITICAL DISCLAIMER:**  
> TrustLens is an **educational risk-awareness tool**, NOT a registered financial advisor (RIA) and NOT a system that issues legally binding scam determinations. It never labels content as "100% scam" or "100% safe".

---

## 2. System Architecture

TrustLens combines deterministic rule-based heuristics with multimodal AI reasoning and an official regulatory knowledge base:

```
┌─────────────────────────────────────────────────────────────┐
│                 React + Vite Client (Tailwind)              │
│       [Message Input / Drag-and-Drop Screenshot / History]   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application Gateway               │
│               [CORS / Validation / Pydantic]                │
└──────────┬───────────────────┬───────────────────┬──────────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌────────────────────┐ ┌───────────────┐ ┌────────────────────┐
│  Risk Engine       │ │  AI Service   │ │ Knowledge Base     │
│  - Guaranteed Gain │ │  - Gemini API │ │  - SEBI Guidelines │
│  - Pressure/Urgency│ │  - OpenAI API │ │  - RBI Directives  │
│  - OTP/PIN Requests│ │  - Intelligent│ │  - NPCI UPI Safety │
│  - Payment Demands │ │    Fallback   │ │  - Swappable RAG   │
└──────────┬─────────┘ └───────┬───────┘ └─────────┬──────────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Fused Decision & Scoring                   │
│         [Cap 100, Categorization, DOs & DON'Ts]             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite Audit Database (trustlens.db)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

* **Frontend:** React 18, Vite, Tailwind CSS, Lucide React icons
* **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2
* **Storage:** SQLite with JSON serialization
* **Vision / OCR:** Pillow, Vision API fallback / PyTesseract support
* **AI Service Layer:** Google Gemini API (`gemini-1.5-flash`) or OpenAI-compatible endpoint with automatic intelligent fallback engine
* **Knowledge Base:** Structured regulatory catalog (`trusted_sources.json`) with an abstract `KnowledgeBaseInterface` ready for FAISS / ChromaDB RAG expansion.

---

## 4. Project Directory Structure

```
trustlens/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ActionGuidance.jsx      # DOs and DON'Ts safety card
│   │   │   ├── AnalysisForm.jsx        # Textarea, file upload & sample preset
│   │   │   ├── ClaimVerification.jsx   # Extracted claims & status badges
│   │   │   ├── Footer.jsx              # Regulatory links & legal disclaimer
│   │   │   ├── HistoryPage.jsx         # Stored verification log
│   │   │   ├── HomeHero.jsx            # Fintech hero section
│   │   │   ├── HowItWorksPage.jsx      # 4-step guide & architecture cards
│   │   │   ├── Navbar.jsx              # Navigation and privacy indicator
│   │   │   ├── RedFlagsCard.jsx        # Severity cards (HIGH/MED/LOW)
│   │   │   ├── ResultDashboard.jsx     # Aggregated verification report
│   │   │   ├── RiskGauge.jsx           # Circular score visualization
│   │   │   ├── TrustedSourcesList.jsx  # Official SEBI & RBI references
│   │   │   └── WhyFlaggedTimeline.jsx  # Numbered reason steps (01, 02..)
│   │   ├── App.jsx                     # State machine & tab controller
│   │   ├── index.css                   # Tailwind styles & fonts
│   │   └── main.jsx                    # React entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   └── database.py             # SQLite persistence layer
│   │   ├── routes/
│   │   │   ├── analyze.py              # /analyze, /analyze-image, /history
│   │   │   └── health.py               # /health endpoint
│   │   ├── services/
│   │   │   ├── ai_service.py           # Gemini/OpenAI API + rule fusion
│   │   │   ├── knowledge_service.py    # Swappable KB interface
│   │   │   ├── ocr_service.py          # Screenshot text extraction
│   │   │   └── risk_engine.py          # Rule heuristics & pattern scoring
│   │   ├── config.py                   # Environment configuration
│   │   ├── main.py                     # FastAPI application setup
│   │   └── schemas.py                  # Pydantic models
│   ├── data/
│   │   └── trusted_sources.json        # Official regulatory knowledge base
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── README.md
└── .gitignore
```

---

## 5. Quickstart & Installation

### Prerequisites
* Python 3.10 or higher
* Node.js v18+ and npm

### 1. Setup and Run Backend

```bash
# Navigate to backend
cd backend

# (Optional) Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Add your Gemini or OpenAI API Key in .env
# If left empty, TrustLens runs seamlessly using the built-in intelligent rule engine!
cp .env.example .env

# Run FastAPI backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will start at: `http://127.0.0.1:8000`  
Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`

### 2. Setup and Run Frontend

In a separate terminal:

```bash
# Navigate to frontend
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend will start at: `http://localhost:5173`

---

## 6. Heuristic Scoring & Risk Bands

TrustLens uses deterministic pattern weights combined with semantic analysis:

| Suspicious Pattern Trigger | Heuristic Weight |
|---|---|
| Confidential Credential / OTP / PIN Request | **+30 points** |
| Guaranteed or Abnormally High Returns (e.g., 25% monthly, double money) | **+25 points** |
| Direct Upfront Payment / Transfer Request | **+20 points** |
| Suspicious Links / Unregulated Telegram or WhatsApp VIP Groups | **+20 points** |
| Artificial Urgency / Pressure Tactics ("Offer valid only today") | **+15 points** |
| Unverified Regulatory Claims ("SEBI approved opportunity") | **+15 points** |

### Risk Bands:
* **`0 – 29` : LOW RISK** — Standard informational content, regular mutual fund notifications, or standard corporate updates.
* **`30 – 59` : NEEDS VERIFICATION** — Ambiguous claims, unregistered tips, or unsubstantiated projections requiring cross-referencing.
* **`60 – 100` : HIGH RISK** — Unsolicited high-yield promises, time-pressure, or payment and credential harvesting.

---

## 7. API Reference

### 1. `POST /api/analyze`
Analyze raw text content.
```json
// Request Body
{
  "text": "SEBI approved investment opportunity. Invest ₹5,000 today and get guaranteed 25% monthly returns."
}

// Response
{
  "id": "c1f7b764-77a8-426b-...",
  "risk_level": "HIGH RISK",
  "risk_score": 75,
  "summary": "This message exhibits critical red-flag patterns characteristic of high-risk unauthorized financial solicitations...",
  "red_flags": [
    {
      "title": "Guaranteed or Unusually High Returns",
      "severity": "HIGH",
      "explanation": "Promises of unusually high, fixed, or guaranteed returns are a primary indicator of deceptive investment schemes...",
      "icon": "TrendingUp"
    }
  ],
  "claims": [
    {
      "claim": "SEBI approved investment opportunity",
      "status": "NEEDS VERIFICATION",
      "explanation": "The message claims regulatory approval from SEBI. SEBI regulates entities but does not endorse specific investment return schemes.",
      "source": "SEBI Registered Intermediary Directory",
      "source_url": "https://www.sebi.gov.in"
    }
  ],
  "why_flagged": [
    { "step_number": "01", "title": "Guaranteed Returns detected", "description": "Identified suspicious trigger phrases: 'guaranteed 25% monthly returns'." }
  ],
  "recommended_actions": [ ... ],
  "action_dos": [ ... ],
  "action_donts": [ ... ],
  "trusted_sources": [ ... ]
}
```

### 2. `POST /api/analyze-image`
Upload screenshot for OCR text extraction and risk analysis.
* **Form Data:** `file`: image file (PNG, JPG, WEBP)

### 3. `GET /api/history`
Retrieve the latest 50 verifications with preview, risk score, and timestamp.

### 4. `GET /api/history/{id}`
Retrieve the full analysis record by unique ID.

### 5. `GET /api/health`
Verify backend service and AI provider connectivity.

---

## 8. Hackathon Demo Walkthrough

1. Open `http://localhost:5173`.
2. Click **"Try a sample"** to instantly load the hackathon sample message:
   ```
   URGENT!!!
   
   SEBI approved investment opportunity.
   Invest ₹5,000 today and get guaranteed 25% monthly returns.
   
   Offer valid only today.
   Send payment to activate your account.
   ```
3. Click **"Analyze Message"**.
4. Observe the **Analysis Result**:
   * Badge: **HIGH RISK**
   * Score: **75 / 100** (Prototype heuristic)
   * Red Flags: **Guaranteed Returns**, **Artificial Urgency**, **Payment Request**, **Regulatory Claim**.
   * Claim Verification: Flags "SEBI approved investment" as **NEEDS VERIFICATION** with links to SEBI's official directory.
   * Why Flagged: Sequential numbered steps (01, 02, 03, 04).
   * What Should I Do: **DOs** and **DON'Ts**.
   * Trusted Information: SEBI, RBI, NPCI benchmarks.
5. Click **"History"** in the top navigation to see the audit log stored in SQLite. Click any item to re-inspect its analysis.
6. Click **"How It Works"** to inspect the 4-step verification flow and the system architecture cards.

---

## 9. License & Attribution

Developed for financial consumer awareness and educational evaluation.  
Official references courtesy of SEBI, RBI, NPCI, and Ministry of Home Affairs Cyber Crime Portal.

