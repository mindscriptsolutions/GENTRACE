# 🧬 GeneTrace – Hereditary Disease Risk Prediction System

<div align="center">

![GeneTrace Banner](https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&q=80)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.3-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.1.3-FF6600?style=for-the-badge)](https://xgboost.readthedocs.io)
[![SHAP](https://img.shields.io/badge/SHAP-Explainable_AI-blueviolet?style=for-the-badge)](https://shap.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A research-grade AI system for hereditary disease risk prediction using pedigree analysis, ensemble machine learning, and explainable AI.**

[Live Demo](#) · [API Docs](http://localhost:8000/api/docs) · [Report Bug](https://github.com/mindscriptsolutions/GENTRACE/issues)

</div>

---

## 📌 Overview

**GeneTrace** is an IEEE-quality final-year research project that predicts hereditary disease risk by analyzing multi-generational family medical history. The system combines paternal and maternal inheritance patterns with personal lifestyle factors to generate risk estimates for:

| Disease | Model | Accuracy | ROC-AUC |
|---|---|---|---|
| 🩸 Type 2 Diabetes | Ensemble (RF + XGB + MLP) | 97.35% | 0.9646 |
| ❤️ Hypertension | Ensemble (RF + XGB + MLP) | 80.84% | 0.8776 |
| 🫀 Cardiovascular Disease | Ensemble (RF + XGB + MLP) | 81.53% | 0.8924 |
| 💇 Androgenetic Alopecia | Ensemble (RF + XGB + MLP) | 80.29% | 0.8706 |
| 🩸 Diabetes Onset Age | Regression | — | MAE: 5.52 yrs |
| 🫀 Heart Onset Age | Regression | — | MAE: 4.38 yrs |

---

## ✨ Key Features

- **🧬 Pedigree Analysis** — Multi-generational family history (parents + grandparents) with disease severity and onset age
- **🤖 Ensemble ML** — Random Forest + XGBoost + MLP combined with soft-voting for robust predictions
- **📐 PWIS Scoring** — Novel Phenotype-Weighted Inheritance Scoring Mechanism (core research contribution)
- **🔍 Explainable AI** — SHAP TreeExplainer on XGBoost base estimator for feature-level explanations
- **💊 RAG Recommendations** — Retrieval-Augmented Generation from WHO, NIH, and CDC knowledge bases
- **📊 Onset Prediction** — Estimates probable age of disease onset based on hereditary patterns
- **📄 PDF Reports** — Downloadable professional health reports with full risk analysis
- **📋 Prediction History** — Full history with filter, view, delete, and PDF download
- **🔐 JWT Authentication** — Secure login/register with 24-hour token expiry

---

## 🧮 PWIS Formula (Research Novelty)

The **Phenotype-Weighted Inheritance Scoring Mechanism (PWIS)** is the core research contribution of GeneTrace:

```
PWIS = Σ [ lineage_weight × (severity_weight + onset_weight) ]

Lineage Weights:
  Parent (1st degree)      = 1.0
  Grandparent (2nd degree) = 0.5

Severity Weights:
  None = 0.00 | Mild = 0.25 | Moderate = 0.60 | Severe = 1.00

Onset Weights:
  Early onset  (< 45 years)  = 1.0
  Mid onset    (45–59 years) = 0.6
  Late onset   (≥ 60 years)  = 0.3
  No disease   (onset = 0)   = 0.0
```

---

## 🗂️ Project Structure

```
GENTRACE/
├── backend/
│   ├── core/
│   │   ├── features.py        # PWIS + interaction feature engineering
│   │   ├── schemas.py         # Pydantic request/response models
│   │   └── security.py        # JWT authentication
│   ├── routers/
│   │   ├── auth.py            # Register / Login / Me
│   │   ├── predict.py         # ML prediction + SHAP + RAG
│   │   ├── history.py         # Prediction history + PDF report
│   │   ├── profile.py         # User profile management
│   │   └── pedigree.py        # Pedigree data
│   └── database.py            # SQLAlchemy models + SQLite
├── models/
│   ├── ensemble_diabetes.pkl
│   ├── ensemble_hypertension.pkl
│   ├── ensemble_heart.pkl
│   ├── ensemble_hairloss.pkl
│   ├── onset_diabetes.pkl
│   └── onset_heart.pkl
├── rag/
│   ├── knowledge_base/        # WHO/NIH/CDC text files
│   └── recommender.py         # RAG retrieval engine
├── templates/                 # HTML pages (self-contained styles)
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── family.html
│   ├── personal.html
│   ├── result.html
│   ├── explainability.html
│   ├── recommendations.html
│   ├── history.html
│   ├── profile.html
│   └── about.html
├── static/
│   ├── css/style.css
│   └── js/
│       ├── app.js             # Auth, API helpers, shared utils
│       └── layout.js          # Sidebar + Navbar injection
├── DATASETS/                  # Training datasets
├── main.py                    # FastAPI app entry point
├── train.py                   # Model training script
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- pip

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/mindscriptsolutions/GENTRACE.git
cd GENTRACE
```

**2. Create and activate virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the server**
```bash
uvicorn main:app --reload
```

**5. Open in browser**
```
http://localhost:8000
```

> ⚠️ Make sure to run `uvicorn` from the **root `GENTRACE/` directory**, not from `backend/`.

---

## 📖 Usage Flow

```
Register → Login → Enter Family History → Enter Personal Info → Run Prediction
                                                                      ↓
                                              View Results → SHAP Explanation
                                                          → Recommendations
                                                          → Download PDF Report
                                                          → View History
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user |
| POST | `/predict/` | Run hereditary risk prediction |
| GET | `/history/` | Get prediction history |
| GET | `/history/{id}/report` | Download PDF report |
| DELETE | `/history/{id}` | Delete prediction record |
| GET | `/profile/` | Get user profile |
| PUT | `/profile/` | Update name or password |
| DELETE | `/profile/` | Delete account |

Full interactive API docs available at: `http://localhost:8000/api/docs`

---

## 🧠 ML Architecture

```
Input: Family History + Personal Info
         ↓
Feature Engineering (PWIS + Interaction Features)
         ↓
┌─────────────────────────────────────┐
│     VotingClassifier (Soft Vote)    │
│  ┌──────────┐ ┌────────┐ ┌───────┐  │
│  │  Random  │ │XGBoost │ │  MLP  │  │
│  │  Forest  │ │        │ │       │  │
│  └──────────┘ └────────┘ └───────┘  │
└─────────────────────────────────────┘
         ↓
Risk Probability + Norwood Stage + Onset Age
         ↓
SHAP Explanation (XGB base estimator)
         ↓
RAG Recommendations (WHO/NIH/CDC KB)
```

---

## 🖥️ Screenshots

| Page | Description |
|---|---|
| Landing Page | Hero with risk demo card |
| Dashboard | Stats, risk cards, recent history |
| Family History | Toggle-based disease input form |
| Prediction Result | Risk scores, PWIS, onset estimates |
| SHAP Explainability | Feature importance bar chart |
| Recommendations | Disease-specific preventive guidance |
| History | Filterable prediction table with PDF download |

---

## ⚠️ Disclaimer

GeneTrace provides **hereditary risk estimates only**. It is **not a medical diagnosis system** and does not use DNA sequencing or genomic analysis. All predictions are probabilistic estimates based on family history patterns. Always consult a qualified healthcare professional for medical advice.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**MindScript Solutions**
- GitHub: [@mindscriptsolutions](https://github.com/mindscriptsolutions)

---

<div align="center">
  <p>Built with ❤️ using FastAPI, XGBoost, SHAP, and RAG</p>
  <p>⭐ Star this repo if you found it useful!</p>
</div>
