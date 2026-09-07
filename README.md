# AI-Based Student Grievance Classification and Smart Routing System

> **A Production-Grade Academic AI & NLP Project for College Reviews, Viva Defense, and Institutional Governance.**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Pytest-26%20Passed-brightgreen.svg)](https://pytest.org/)

---

## 1. Executive Summary

In traditional university administration, student complaints and campus queries are managed through physical paper slips, generic email mailboxes, or cumbersome drop-down forms where students are forced to guess which maintenance or administrative department is responsible. This leads to misrouted tickets, delayed response times, poor SLA compliance, and zero auditability.

The **AI-Based Student Grievance Classification and Smart Routing System** solves this by combining:
1. **Natural Language Processing (NLP)**: Supervised text classification using **TF-IDF (unigrams + bigrams)** and **Multinomial Logistic Regression** trained on a curated corpus of 1,260 realistic student grievances across 9 operational categories.
2. **Safety-First Confidence Fallback**: A strict **70% confidence threshold**. When input text is ambiguous, novel, or out-of-domain, the system automatically routes the ticket to the **General Helpdesk / Admin Manual Review Queue** rather than making hallucinated or low-confidence assignments.
3. **Transparent Rule-Based Priority Engine**: Unlike "black-box" neural networks that make arbitrary severity decisions, safety priority (**High**, **Medium**, **Low**) is governed by an **explicit, deterministic keyword heuristic engine** targeting physical safety hazards (e.g., electrical sparks, stuck elevators, water flooding, food contamination).
4. **Streamlined Two-Role Architecture**: Designed specifically for clean academic demonstration and institutional realism:
   - 👨‍🎓 **Student**: Submits natural language grievances without picking departments, receives instant AI predictions, and tracks personal ticket history.
   - 🛠️ **Central Administrator**: Holds executive oversight across all 9 departmental routing queues, manages status transitions with audit remarks, triages low-confidence fallbacks, and inspects model performance.
5. **Modern Institutional User Interface**: Built with **React 18**, **Vite**, **TypeScript**, and **Recharts**, adhering to institutional software design standards (Navy `#1F4E79`, crisp data tables, and zero sci-fi animations or artificial gradients).

---

## 2. System Architecture

```text
                                 [ Student Grievance Text Input ]
                                 (Title + Natural Language Text)
                                               |
                                               v
                                [ Text Preprocessing & Cleaning ]
                                 (lowercase, punct, whitespace)
                                               |
                                               v
                                   [ TF-IDF Feature Extraction ]
                                     (unigrams + bigrams: 3,450+)
                                               |
                                               v
                                  [ Logistic Regression Engine ]
                                               |
                     +-------------------------+-------------------------+
                     |                                                   |
           Confidence >= 0.70                                   Confidence < 0.70
                     |                                                   |
                     v                                                   v
          [ Direct Category Match ]                        [ Fallback: Other / Manual Review ]
                     |                                                   |
                     +-------------------------+-------------------------+
                                               |
                                               v
                                 [ Priority Engine (Rule-Based) ]
                                (High: Safety Hazard / Med / Low)
                                               |
                                               v
                             [ Deterministic Routing Matrix ]
                                (Category -> Department Code)
                                               |
                                               v
                             [ SQLite Database & Audit Trail ]
                                               |
                     +-------------------------+-------------------------+
                     |                                                   |
                     v                                                   v
            [ Student Portal ]                                  [ Admin Portal ]
        - Lodge new grievance                               - Operations KPI analytics
        - No department selection needed                    - Department queues filter
        - Real-time AI prediction & confidence              - Status update with resolution remarks
        - Immutable status history timeline                 - Manual Review triage queue
                                                            - Model performance & live sandbox
```

---

## 3. Dataset Specifications

The dataset is located at `backend/data/grievances.csv` and contains **1,260 balanced records** across 9 operational categories (140 records per class):

| Category | Typical Student Issues Included | Routed Department |
| :--- | :--- | :--- |
| **IT / Network** | Wi-Fi disconnects, DNS errors, slow internet, LAN port dead, ERP 500 error, Moodle down | IT & Network Services (`DEPT-IT`) |
| **Electrical** | Sparking switches, tube lights flickering, ceiling fan noise, MCB tripped, AC blowing warm air | Electrical Maintenance (`DEPT-ELEC`) |
| **Plumbing** | Ceiling pipe leak, flush valve broken, washbasin clogged, water cooler murky, low pressure | Plumbing & Water Works (`DEPT-PLUMB`) |
| **Cleaning / Housekeeping** | Unhygienic restrooms, overflowing dustbins, dusty desks, dried beverage spills, uncleaned stairs | Sanitation & Housekeeping (`DEPT-HOUSEKEEPING`) |
| **Laboratory** | Oscilloscope error, microscope light burnt, out-of-stock reagents, fume hood off, lathe stuck | Laboratory & Technical Infra (`DEPT-LAB`) |
| **Infrastructure / Maintenance** | Broken bench nails, cracked window panes, jammed door locks, falling ceiling plaster, elevator stuck | Estate & Civil Infrastructure (`DEPT-INFRA`) |
| **Academic** | Grade discrepancy, marks missing on portal, timetable elective clash, attendance shortage glitch | Academic Affairs & Examination (`DEPT-ACADEMIC`) |
| **Hostel / Canteen** | Worms in mess food, stale food, canteen overcharging MRP, broken laundry machines, door latch | Hostel Administration & Dining (`DEPT-HOSTEL`) |
| **Other / Manual Review** | Ambiguous queries, lost ID cards/backpacks, bus route timing delays, fest poster permissions | General Helpdesk / Admin (`DEPT-ADMIN`) |

*Dataset Quality Features*: Includes realistic student abbreviations (`cse lab`, `wifi`, `lan`, `lms`), common typos (`problm`, `brokn`, `complnt`), varied sentence lengths, and locations across campus blocks.

---

## 4. Machine Learning Pipeline & Empirical Benchmarks

The model training pipeline is implemented in `backend/app/ml/train.py` and uses an **80/20 stratified split** (1,008 train / 252 test) with **no data leakage** (the TF-IDF vectorizer is fit strictly on training data).

### Candidate Model Comparison (Test Set Evaluation)

| Algorithm | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | Production Selection |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Logistic Regression** | **98.8%** | **0.9891** | **0.9881** | **0.9884** | **0.9881** | **Selected** (Calibrated soft probabilities & explainability) |
| **Multinomial Naive Bayes** | 98.4% | 0.9852 | 0.9841 | 0.9844 | 0.9841 | Baseline benchmark |
| **Linear SVC (Calibrated)** | 98.4% | 0.9852 | 0.9841 | 0.9844 | 0.9841 | Baseline benchmark |

*Artifacts Saved in `backend/app/artifacts/`*:
- `model.joblib`: Trained Multinomial Logistic Regression model (`C=10.0`, `class_weight='balanced'`)
- `vectorizer.joblib`: Fitted TF-IDF Vectorizer (sublinear TF scaling, unigrams + bigrams)
- `label_encoder.joblib`: LabelEncoder mapping class names to indices
- `metadata.json`: Complete metrics, confusion matrix, and training metadata

---

## 5. Demo Credentials for Viva / Evaluation

The database is pre-seeded with **44 realistic grievances** and 2 primary user accounts with secure bcrypt hashes:

| Role | Display Identity | Email | Password | Scope & Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| **Student** | Aarav Patel | `student@college.local` | `Student@123` | File natural-language complaints, view personal tickets & audit history |
| **Admin** | System Administrator | `admin@college.local` | `Admin@123` | Global operations, department queue filtering, status update, manual review, live ML tester |

> **Viva Tip**: The login page provides **One-Click Fast Demo Buttons** that instantly fill credentials for both Student and Admin roles.

---

## 6. Step-by-Step Local Setup & Execution

### Prerequisites
- Python 3.11+
- Node.js v18+ with npm

### Quick Start (One-Click Windows Batch Scripts)
Double-click:
1. `run_backend.bat`: Launches the FastAPI server on `http://127.0.0.1:8000`
2. `run_frontend.bat`: Launches the React + Vite frontend on `http://localhost:5173`

---

### Manual Setup (PowerShell)

#### Step 1: Backend Setup
```powershell
cd c:\Users\koneAjay\OneDrive\Desktop\AI-SGC-system\backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install -r requirements.txt

# Train ML model and generate artifacts
$env:PYTHONPATH = "c:\Users\koneAjay\OneDrive\Desktop\AI-SGC-system\backend"
python -m app.ml.train

# Seed database with demo records
python scripts\seed_demo_data.py

# Run backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI documentation: `http://127.0.0.1:8000/docs`

#### Step 2: Frontend Setup
```powershell
cd c:\Users\koneAjay\OneDrive\Desktop\AI-SGC-system\frontend

# Ensure Node LTS is on PATH
$env:PATH = "C:\Users\koneAjay\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.19.0-win-x64;" + $env:PATH

# Run Vite dev server
npm run dev
```
Frontend UI will be live at: `http://localhost:5173`

---

## 7. Running Automated Test Suite

The project includes 26 automated unit and integration tests covering ML preprocessing, inference thresholds, priority heuristics, routing matrix, authentication, status validation, deletion-safe ticket numbering, and RBAC isolation:

```powershell
cd c:\Users\koneAjay\OneDrive\Desktop\AI-SGC-system\backend
$env:PYTHONPATH = "c:\Users\koneAjay\OneDrive\Desktop\AI-SGC-system\backend"
.\venv\Scripts\pytest.exe -v tests
```

### Verified Test Results:
```text
tests/test_auth.py::test_student_login_success PASSED                     [  3%]
tests/test_auth.py::test_admin_login_success PASSED                       [  7%]
tests/test_auth.py::test_login_failure PASSED                             [ 11%]
tests/test_auth.py::test_get_me_authorized PASSED                         [ 15%]
tests/test_auth.py::test_get_me_unauthorized PASSED                       [ 19%]
tests/test_grievances.py::test_submit_grievance_success PASSED            [ 23%]
tests/test_grievances.py::test_submit_grievance_validation_error PASSED   [ 26%]
tests/test_grievances.py::test_get_my_grievances PASSED                   [ 30%]
tests/test_grievances.py::test_rbac_student_isolation PASSED              [ 34%]
tests/test_grievances.py::test_admin_department_queue_filtering PASSED    [ 38%]
tests/test_grievances.py::test_admin_status_update_and_history PASSED     [ 42%]
tests/test_grievances.py::test_admin_endpoints PASSED                     [ 46%]
tests/test_grievances.py::test_admin_view_all_grievances PASSED           [ 50%]
tests/test_grievances.py::test_duplicate_status_update_rejected PASSED   [ 53%]
tests/test_grievances.py::test_manual_review_history_records_correct_previous_status PASSED [ 57%]
tests/test_grievances.py::test_ticket_number_uniqueness_on_deletion PASSED [ 61%]
tests/test_ml.py::test_clean_text_normal PASSED                           [ 65%]
tests/test_ml.py::test_clean_text_edge_cases PASSED                       [ 69%]
tests/test_ml.py::test_classifier_is_ready PASSED                         [ 73%]
tests/test_ml.py::test_classifier_prediction_structure PASSED             [ 76%]
tests/test_ml.py::test_classifier_threshold_fallback PASSED               [ 80%]
tests/test_ml.py::test_classifier_top_3_probabilities PASSED              [ 84%]
tests/test_priority_routing.py::test_priority_high_safety_keywords PASSED [ 88%]
tests/test_priority_routing.py::test_priority_medium_operational_keywords PASSED [ 92%]
tests/test_priority_routing.py::test_priority_low_default PASSED          [ 96%]
tests/test_priority_routing.py::test_routing_all_categories PASSED        [100%]

======================= 26 passed in 3.86s ========================
```

---

## 8. Directory Hierarchy

```text
AI-SGC-system/
├── backend/
│   ├── app/
│   │   ├── artifacts/                 # Serialized model, vectorizer, label encoder, metadata.json
│   │   ├── ml/
│   │   │   ├── preprocessing.py       # Regex text cleaning & normalization
│   │   │   ├── train.py               # Model training & cross-algorithm evaluation
│   │   │   └── predict.py             # Inference engine with 70% threshold fallback
│   │   ├── models/
│   │   │   └── models.py              # SQLAlchemy ORM (User, Dept, Grievance, History, Prediction)
│   │   ├── schemas/
│   │   │   └── schemas.py             # Pydantic v2 validation models
│   │   ├── services/
│   │   │   ├── auth.py                # JWT & Bcrypt RBAC
│   │   │   ├── routing.py             # Deterministic category -> department mapper
│   │   │   └── priority.py            # Rule-based priority heuristic engine
│   │   ├── routers/
│   │   │   ├── auth.py                # Login & /me endpoints
│   │   │   ├── grievances.py          # Student filing & retrieval
│   │   │   ├── department.py          # Department queue viewer & status updater
│   │   │   └── admin.py               # Analytics, model evaluation & live tester
│   │   ├── config.py                  # Pydantic settings & DB connection
│   │   ├── database.py                # SQLAlchemy engine & session factory
│   │   └── main.py                    # FastAPI application entrypoint
│   ├── data/
│   │   └── grievances.csv             # 1,260 balanced curated training records
│   ├── scripts/
│   │   ├── generate_dataset.py        # Dataset generator script
│   │   └── seed_demo_data.py          # Database seeding script (44 demo grievances)
│   └── tests/                         # Pytest test suite (21 tests)
├── frontend/
│   ├── src/
│   │   ├── components/                # Navbar, StatusBadge, PriorityBadge, ConfidenceMeter
│   │   ├── context/                   # AuthContext with JWT management
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx          # Dual-role tabbed login with demo accounts
│   │   │   ├── StudentDashboard.tsx   # Grievance filing & personal tracking
│   │   │   ├── GrievanceDetailPage.tsx# Full audit history & timeline
│   │   │   ├── AdminDashboard.tsx     # KPI analytics, department queues, embedded ML tester
│   │   │   ├── AdminManualReview.tsx  # Low-confidence fallback triage queue
│   │   │   └── AdminModelPerformance.tsx# Model metrics, benchmarks, live sandbox
│   │   ├── services/api.ts            # Axios client with JWT interceptor
│   │   └── types/index.ts             # TypeScript interfaces
│   └── package.json
├── run_backend.bat                    # Windows one-click backend runner
├── run_frontend.bat                   # Windows one-click frontend runner
├── README.md                          # Project overview & quickstart
└── PROJECT_DOCUMENTATION.md           # 28-Chapter report & viva defense guide
```

---

## 9. Key Viva Defense Points

1. **Why Two Roles?**: Eliminates the distraction of logging into separate staff accounts during a presentation while maintaining 100% realistic institutional departmental routing. All 9 departments exist as operational queues managed centrally by the Administrator.
2. **Why Not BERT/LLM?**: TF-IDF + Logistic Regression gives sub-10ms inference latency, zero GPU dependencies, explainable feature weights, and well-calibrated probabilities for threshold fallback.
3. **Deterministic Safety**: Priority (High/Medium/Low) is rule-based keyword heuristics, NOT black-box ML, ensuring physical emergencies (sparks, leaks, stuck elevators) are never misclassified as low priority.
4. **Safety Fallback**: Any complaint scoring below 70% confidence is automatically redirected to the Admin Manual Review queue.
