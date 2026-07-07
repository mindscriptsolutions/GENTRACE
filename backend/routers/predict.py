import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db, PredictionHistory, User
from backend.core.schemas import PredictionInput, PredictionOut
from backend.core.security import get_current_user
from backend.core.features import compute_features
from rag.recommender import get_recommendation

router = APIRouter(prefix="/predict", tags=["Prediction"])

MODELS_DIR = Path("models")

# ── Lazy-load models once ─────────────────────────────────────────────────────
_models: dict = {}

def _load_models():
    if _models:
        return
    required = [
        "ensemble_diabetes.pkl", "ensemble_hypertension.pkl",
        "ensemble_heart.pkl",    "ensemble_hairloss.pkl",
        "onset_diabetes.pkl",    "onset_heart.pkl",
        "feature_columns.json",
    ]
    missing = [f for f in required if not (MODELS_DIR / f).exists()]
    if missing:
        raise HTTPException(
            status_code=503,
            detail=f"Models not yet trained. Missing: {missing}. Run the training notebook first."
        )
    _models["diabetes"]      = joblib.load(MODELS_DIR / "ensemble_diabetes.pkl")
    _models["hypertension"]  = joblib.load(MODELS_DIR / "ensemble_hypertension.pkl")
    _models["heart"]         = joblib.load(MODELS_DIR / "ensemble_heart.pkl")
    _models["hairloss"]      = joblib.load(MODELS_DIR / "ensemble_hairloss.pkl")
    _models["onset_diabetes"]= joblib.load(MODELS_DIR / "onset_diabetes.pkl")
    _models["onset_heart"]   = joblib.load(MODELS_DIR / "onset_heart.pkl")
    with open(MODELS_DIR / "feature_columns.json") as f:
        _models["feature_cols"] = json.load(f)


def _to_df(features: dict, model) -> pd.DataFrame:
    cols = list(model.feature_names_in_)
    row = {c: features.get(c, 0) for c in cols}
    return pd.DataFrame([row])


@router.post("/", response_model=PredictionOut)
def predict(payload: PredictionInput,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):

    _load_models()
    features = compute_features(payload)

    diabetes_risk    = float(_models["diabetes"].predict_proba(_to_df(features, _models["diabetes"]))[0][1])
    hypertension_risk= float(_models["hypertension"].predict_proba(_to_df(features, _models["hypertension"]))[0][1])
    heart_risk       = float(_models["heart"].predict_proba(_to_df(features, _models["heart"]))[0][1])
    hair_norwood     = int(_models["hairloss"].predict(_to_df(features, _models["hairloss"]))[0])
    onset_diabetes   = float(_models["onset_diabetes"].predict(_to_df(features, _models["onset_diabetes"]))[0])
    onset_heart      = float(_models["onset_heart"].predict(_to_df(features, _models["onset_heart"]))[0])

    # ── SHAP explanation (use XGB base estimator from diabetes ensemble) ──────
    try:
        import shap
        xgb_model  = _models["diabetes"].named_estimators_["xgb"]
        X_shap     = _to_df(features, _models["diabetes"])
        explainer  = shap.TreeExplainer(xgb_model)
        shap_vals  = explainer.shap_values(X_shap)
        cols       = list(_models["diabetes"].feature_names_in_)
        sv         = shap_vals[0] if not isinstance(shap_vals, list) else shap_vals[1][0]
        if hasattr(sv, '__len__') and len(sv.shape) > 1:
            sv = sv[0]
        shap_dict  = {col: round(float(sv[i]), 4) for i, col in enumerate(cols)}
        shap_top   = dict(sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:10])
    except Exception:
        shap_top = {}

    # ── RAG recommendation ────────────────────────────────────────────────────
    recommendation = get_recommendation(
        diabetes_risk=diabetes_risk,
        hypertension_risk=hypertension_risk,
        heart_risk=heart_risk,
        hair_norwood=hair_norwood,
        features=features,
    )

    # ── Persist to history ────────────────────────────────────────────────────
    record = PredictionHistory(
        user_id=current_user.id,
        diabetes_risk=diabetes_risk,
        hypertension_risk=hypertension_risk,
        heart_risk=heart_risk,
        hair_loss_norwood=hair_norwood,
        onset_diabetes=onset_diabetes,
        onset_heart=onset_heart,
        shap_json=json.dumps(shap_top),
        recommendation=recommendation,
    )
    db.add(record)
    db.commit()

    return PredictionOut(
        diabetes_risk=round(diabetes_risk, 4),
        hypertension_risk=round(hypertension_risk, 4),
        heart_risk=round(heart_risk, 4),
        hair_loss_norwood=hair_norwood,
        onset_diabetes_years=round(onset_diabetes, 1),
        onset_heart_years=round(onset_heart, 1),
        pwis_diabetes=features["PWIS_Diabetes"],
        pwis_heart=features["PWIS_HeartDisease"],
        paternal_score=features["Paternal_Score"],
        maternal_score=features["Maternal_Score"],
        family_disease_count=features["Family_Disease_Count"],
        shap_values=shap_top,
        recommendation=recommendation,
    )
