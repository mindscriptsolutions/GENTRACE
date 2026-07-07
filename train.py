"""
GeneTrace - Local Training Script
===================================
Trains ensemble models (RF + XGBoost + MLP) for:
  - Diabetes classification
  - Hypertension classification
  - Cardiovascular disease classification
  - Hair loss Norwood stage classification
  - Onset age regression (Diabetes, Heart)

Saves all models + feature_columns.json to models/
Run: python train.py
"""

import sys
import json
import warnings
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, VotingClassifier, VotingRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, confusion_matrix,
                              mean_absolute_error, mean_squared_error)
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier, XGBRegressor

warnings.filterwarnings("ignore")
np.random.seed(42)

DATASETS = Path("DATASETS")
MODELS   = Path("models")
MODELS.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Load & preprocess public datasets
# ─────────────────────────────────────────────────────────────────────────────

def load_diabetes():
    df = pd.read_csv(DATASETS / "diabetes_prediction_dataset.csv")
    df["gender"] = (df["gender"] == "Male").astype(int)
    df["smoking_history"] = df["smoking_history"].map(
        {"never": 0, "No Info": 0, "former": 1, "current": 2, "ever": 1, "not current": 1}
    ).fillna(0)
    df = df.rename(columns={
        "gender": "Gender", "age": "Age", "bmi": "BMI",
        "hypertension": "Father_Hypertension",
        "heart_disease": "Father_HeartDisease",
        "smoking_history": "Smoker",
        "HbA1c_level": "HbA1c",
        "blood_glucose_level": "Blood_Glucose",
        "diabetes": "Target_Diabetes",
    })
    df["Alcohol"]        = 0
    df["Exercise_Level"] = 1
    df["Diet_Quality"]   = 1
    df["Sleep_Hours"]    = 7.0
    df["Stress_Level"]   = 5
    return df


def load_hypertension():
    df = pd.read_csv(DATASETS / "hypertension_dataset.csv")
    df["Gender"]                  = (df["Gender"] == "Male").astype(int)
    df["Smoking_Status"]          = df["Smoking_Status"].map({"Never": 0, "Former": 1, "Current": 2}).fillna(0)
    df["Physical_Activity_Level"] = df["Physical_Activity_Level"].map({"Low": 0, "Moderate": 1, "High": 2}).fillna(1)
    df["Family_History"]          = (df["Family_History"] == "Yes").astype(int)
    df["Diabetes"]                = (df["Diabetes"] == "Yes").astype(int)
    df["Hypertension"]            = df["Hypertension"].map({"Low": 0, "Normal": 0, "High": 1,
                                                             "Yes": 1, "No": 0, 1: 1, 0: 0}).fillna(0).astype(int)
    df = df.rename(columns={
        "Smoking_Status": "Smoker",
        "Alcohol_Intake": "Alcohol",
        "Physical_Activity_Level": "Exercise_Level",
        "Sleep_Duration": "Sleep_Hours",
        "Family_History": "Family_Hypertension_Flag",
        "Hypertension": "Target_Hypertension",
    })
    df = df.drop(columns=[c for c in ["Country", "Education_Level", "Employment_Status"] if c in df.columns])
    df["Diet_Quality"] = 1
    return df


def load_cardio():
    df = pd.read_csv(DATASETS / "cardio_train.csv", sep=";")
    df = df.drop(columns=["id"])
    df["age"]    = (df["age"] / 365).round(0).astype(int)
    df["gender"] = (df["gender"] == 2).astype(int)
    df = df.rename(columns={
        "age": "Age", "gender": "Gender", "weight": "Weight",
        "height": "Height", "ap_hi": "Systolic_BP", "ap_lo": "Diastolic_BP",
        "cholesterol": "Cholesterol", "gluc": "Glucose",
        "smoke": "Smoker", "alco": "Alcohol", "active": "Exercise_Level",
        "cardio": "Target_HeartDisease",
    })
    df["BMI"] = (df["Weight"] / ((df["Height"] / 100) ** 2)).round(1).clip(14, 50)
    df = df.drop(columns=["Weight", "Height"])
    df["Diet_Quality"] = 1
    df["Sleep_Hours"]  = 7.0
    df["Stress_Level"] = 5
    return df


def load_hair():
    df = pd.read_csv(DATASETS / "hair_loss.csv")
    norwood_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 6, 5: 7}
    df["Target_HairLoss_Norwood"] = df["hair_fall"].map(norwood_map).fillna(1).astype(int)
    df = df.drop(columns=["hair_fall"])
    return df


def load_pedigree():
    df = pd.read_csv(DATASETS / "pedigree_dataset.csv")
    df["Gender"] = (df["Gender"] == "Male").astype(int)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. Build feature matrices
# ─────────────────────────────────────────────────────────────────────────────

def _merge(public_df, ped_cols, ped_df, target_col):
    ped = ped_df[ped_cols + [target_col]].copy()
    n   = min(len(public_df), len(ped))
    pub = public_df.sample(n, random_state=42).reset_index(drop=True)
    p   = ped.sample(n, random_state=42).reset_index(drop=True).drop(columns=[target_col])
    # Drop pedigree cols that already exist in public df to avoid duplicates
    p = p.drop(columns=[c for c in p.columns if c in pub.columns], errors="ignore")
    merged = pd.concat([pub, p], axis=1)
    feat_cols = [c for c in merged.columns if c != target_col]
    X = merged[feat_cols].fillna(0)
    y = merged[target_col].astype(int)
    return X, y, feat_cols


def build_diabetes_features(diab_df, ped_df):
    ped_cols = [
        "Father_Diabetes", "Mother_Diabetes",
        "Father_Hypertension", "Mother_Hypertension",
        "Paternal_Grandfather_Diabetes", "Paternal_Grandmother_Diabetes",
        "Maternal_Grandfather_Diabetes", "Maternal_Grandmother_Diabetes",
        "Father_Diabetes_Severity", "Mother_Diabetes_Severity",
        "Father_Diabetes_Onset", "Mother_Diabetes_Onset",
        "Paternal_Score", "Maternal_Score", "Family_Disease_Count", "PWIS_Diabetes",
    ]
    return _merge(diab_df, ped_cols, ped_df, "Target_Diabetes")


def build_hypertension_features(hyp_df, ped_df):
    """
    The public hypertension dataset has near-zero feature-target correlation
    (synthetic dataset with random labels). Train purely on pedigree data
    which has properly correlated hereditary + lifestyle risk factors.
    """
    feat_cols = [
        "Father_Hypertension", "Mother_Hypertension",
        "Father_Diabetes", "Mother_Diabetes",
        "BMI", "Smoker", "Alcohol", "Exercise_Level",
        "Diet_Quality", "Sleep_Hours", "Stress_Level",
        "Paternal_Score", "Maternal_Score",
        "Family_Disease_Count", "PWIS_Diabetes",
        "Age", "Gender",
    ]
    # Interaction features
    df = ped_df.copy()
    df["Both_Parents_Hyp"]   = df["Father_Hypertension"] * df["Mother_Hypertension"]
    df["HighBMI_x_FamHyp"]  = (df["BMI"] > 28).astype(int) * (df["Father_Hypertension"] + df["Mother_Hypertension"])
    df["Stress_x_FamHyp"]   = (df["Stress_Level"] >= 7).astype(int) * (df["Father_Hypertension"] + df["Mother_Hypertension"])
    feat_cols = feat_cols + ["Both_Parents_Hyp", "HighBMI_x_FamHyp", "Stress_x_FamHyp"]
    X = df[feat_cols].fillna(0)
    y = df["Target_Hypertension"].astype(int)
    # SMOTE to balance
    sm = SMOTE(random_state=42)
    X_res, y_res = sm.fit_resample(X, y)
    return pd.DataFrame(X_res, columns=feat_cols), pd.Series(y_res), feat_cols


def build_heart_features(cardio_df, ped_df):
    """
    Train on pedigree data (correlated hereditary risk) merged with
    cardio clinical features for the strongest combined signal.
    Also adds interaction features between PWIS and clinical risk factors.
    """
    feat_cols = [
        "Father_HeartDisease", "Mother_HeartDisease",
        "Father_Heart_Severity", "Mother_Heart_Severity",
        "Father_Heart_Onset", "Mother_Heart_Onset",
        "Father_Hypertension", "Mother_Hypertension",
        "BMI", "Smoker", "Alcohol", "Exercise_Level",
        "Diet_Quality", "Sleep_Hours", "Stress_Level",
        "Age", "Gender",
        "Paternal_Score", "Maternal_Score",
        "Family_Disease_Count", "PWIS_HeartDisease",
    ]
    df = ped_df.copy()
    # Interaction features
    df["Both_Parents_Heart"]  = df["Father_HeartDisease"] * df["Mother_HeartDisease"]
    df["PWIS_x_Smoker"]       = df["PWIS_HeartDisease"] * df["Smoker"]
    df["PWIS_x_HighBMI"]      = df["PWIS_HeartDisease"] * (df["BMI"] > 28).astype(int)
    df["EarlyOnset_Father"]   = (df["Father_Heart_Onset"].between(1, 50)).astype(int)
    df["EarlyOnset_Mother"]   = (df["Mother_Heart_Onset"].between(1, 50)).astype(int)
    df["HighRisk_Combined"]   = (
        (df["Father_HeartDisease"] + df["Mother_HeartDisease"]) *
        df["Father_Heart_Severity"] * (df["BMI"] > 28).astype(int)
    )
    feat_cols = feat_cols + ["Both_Parents_Heart", "PWIS_x_Smoker", "PWIS_x_HighBMI",
                             "EarlyOnset_Father", "EarlyOnset_Mother", "HighRisk_Combined"]
    X = df[feat_cols].fillna(0)
    y = df["Target_HeartDisease"].astype(int)
    sm = SMOTE(random_state=42)
    X_res, y_res = sm.fit_resample(X, y)
    return pd.DataFrame(X_res, columns=feat_cols), pd.Series(y_res), feat_cols


def build_hairloss_features(ped_df):
    """
    Train purely on pedigree data.
    Binary target: 0 = Norwood stage 1 (no significant loss), 1 = stage 2+ (hereditary loss).
    Uses SMOTE to balance classes.
    Adds interaction features to strengthen hereditary signal.
    """
    feat_cols = [
        "Gender", "Age",
        "Father_HairLoss", "Mother_HairLoss",
        "Paternal_Grandfather_HairLoss", "Maternal_Grandfather_HairLoss",
        "Paternal_Score", "Maternal_Score",
        "Smoker", "Stress_Level",
    ]
    df = ped_df.copy()
    df["Target_HairLoss_Binary"] = (df["Target_HairLoss_Norwood"] >= 2).astype(int)

    # Interaction features: male + paternal hair loss is the strongest hereditary signal
    df["Male_x_FatherHL"]  = df["Gender"] * df["Father_HairLoss"]
    df["Male_x_PGF_HL"]    = df["Gender"] * df["Paternal_Grandfather_HairLoss"]
    df["Age_x_FatherHL"]   = df["Age"]    * df["Father_HairLoss"]
    df["Both_Grandfathers"]= df["Paternal_Grandfather_HairLoss"] * df["Maternal_Grandfather_HairLoss"]
    df["Both_Parents"]     = df["Father_HairLoss"] * df["Mother_HairLoss"]

    feat_cols = feat_cols + ["Male_x_FatherHL", "Male_x_PGF_HL",
                             "Age_x_FatherHL", "Both_Grandfathers", "Both_Parents"]
    X = df[feat_cols].fillna(0)
    y = df["Target_HairLoss_Binary"]
    sm = SMOTE(random_state=42)
    X_res, y_res = sm.fit_resample(X, y)
    return pd.DataFrame(X_res, columns=feat_cols), pd.Series(y_res), feat_cols


def build_onset_features(ped_df, disease):
    df = ped_df.copy()
    if disease == "diabetes":
        onset_col = "Father_Diabetes_Onset"
        feat_cols = [
            "Father_Diabetes", "Mother_Diabetes",
            "Father_Diabetes_Severity", "Mother_Diabetes_Severity",
            "Paternal_Grandfather_Diabetes", "Paternal_Grandmother_Diabetes",
            "Maternal_Grandfather_Diabetes", "Maternal_Grandmother_Diabetes",
            "PWIS_Diabetes", "Paternal_Score", "Maternal_Score",
            "BMI", "Smoker", "Exercise_Level", "Diet_Quality",
        ]
    else:
        onset_col = "Father_Heart_Onset"
        feat_cols = [
            "Father_HeartDisease", "Mother_HeartDisease",
            "Father_Heart_Severity", "Mother_Heart_Severity",
            "PWIS_HeartDisease", "Paternal_Score", "Maternal_Score",
            "BMI", "Smoker", "Exercise_Level",
        ]
    df = df[df[onset_col] > 0].copy()
    return df[feat_cols].fillna(0), df[onset_col].astype(float), feat_cols


# ─────────────────────────────────────────────────────────────────────────────
# 3. Ensemble builders
# ─────────────────────────────────────────────────────────────────────────────

def make_classifier(scale_pos_weight=1.0, class_weight=None):
    rf  = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42,
                                  class_weight=class_weight, n_jobs=-1)
    xgb = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.05,
                        eval_metric="logloss", scale_pos_weight=scale_pos_weight,
                        random_state=42)
    mlp = Pipeline([
        ("scaler", StandardScaler()),
        ("mlp", MLPClassifier(hidden_layer_sizes=(128, 64, 32), activation="relu",
                              max_iter=300, random_state=42, early_stopping=True)),
    ])
    return VotingClassifier(estimators=[("rf", rf), ("xgb", xgb), ("mlp", mlp)],
                            voting="soft", n_jobs=1)


def make_regressor():
    rf  = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
    xgb = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05,
                       random_state=42)
    mlp = Pipeline([
        ("scaler", StandardScaler()),
        ("mlp", MLPRegressor(hidden_layer_sizes=(128, 64, 32), activation="relu",
                             max_iter=300, random_state=42, early_stopping=True)),
    ])
    return VotingRegressor(estimators=[("rf", rf), ("xgb", xgb), ("mlp", mlp)], n_jobs=1)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def eval_classifier(model, X_test, y_test, name):
    y_pred   = model.predict(X_test)
    n_classes = len(np.unique(y_test))
    avg      = "binary" if n_classes == 2 else "weighted"
    print(f"\n{'='*52}")
    print(f"  {name}")
    print(f"{'='*52}")
    print(f"  Accuracy  : {accuracy_score(y_test, y_pred):.4f}")
    print(f"  Precision : {precision_score(y_test, y_pred, average=avg, zero_division=0):.4f}")
    print(f"  Recall    : {recall_score(y_test, y_pred, average=avg, zero_division=0):.4f}")
    print(f"  F1 Score  : {f1_score(y_test, y_pred, average=avg, zero_division=0):.4f}")
    if n_classes == 2:
        y_proba = model.predict_proba(X_test)[:, 1]
        print(f"  ROC-AUC   : {roc_auc_score(y_test, y_proba):.4f}")
    else:
        y_proba = model.predict_proba(X_test)
        print(f"  ROC-AUC   : {roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted'):.4f}")
    print(f"  Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")


def eval_regressor(model, X_test, y_test, name):
    y_pred = model.predict(X_test)
    print(f"\n{'='*52}")
    print(f"  {name}")
    print(f"{'='*52}")
    print(f"  MAE  : {mean_absolute_error(y_test, y_pred):.2f} years")
    print(f"  RMSE : {np.sqrt(mean_squared_error(y_test, y_pred)):.2f} years")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Train & save
# ─────────────────────────────────────────────────────────────────────────────

def train_task(name, X, y, task="classify", scale_pos_weight=1.0, class_weight=None):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42,
        stratify=y if task == "classify" else None,
    )
    if task == "classify":
        model = make_classifier(scale_pos_weight=scale_pos_weight, class_weight=class_weight)
    else:
        model = make_regressor()
    print(f"\n>> Training {name}  |  train={len(X_train)}  test={len(X_test)}")
    model.fit(X_train, y_train)
    if task == "classify":
        eval_classifier(model, X_test, y_test, name)
    else:
        eval_regressor(model, X_test, y_test, name)
    out = MODELS / f"{name}.pkl"
    joblib.dump(model, out)
    print(f"  [SAVED] {out}")
    return model


# ─────────────────────────────────────────────────────────────────────────────
# 6. Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading datasets...")
    diab_df    = load_diabetes()
    hyp_df     = load_hypertension()
    cardio_df  = load_cardio()
    hair_df    = load_hair()
    ped_df     = load_pedigree()
    print("  [OK] All datasets loaded.")

    X, y, _ = build_diabetes_features(diab_df, ped_df)
    train_task("ensemble_diabetes", X, y, "classify")

    X, y, _ = build_hypertension_features(hyp_df, ped_df)
    train_task("ensemble_hypertension", X, y, "classify", class_weight="balanced")

    X, y, _ = build_heart_features(cardio_df, ped_df)
    train_task("ensemble_heart", X, y, "classify")

    X, y, _ = build_hairloss_features(ped_df)
    train_task("ensemble_hairloss", X, y, "classify", class_weight="balanced")

    X, y, _ = build_onset_features(ped_df, "diabetes")
    train_task("onset_diabetes", X, y, "regress")

    X, y, _ = build_onset_features(ped_df, "heart")
    train_task("onset_heart", X, y, "regress")

    inference_cols = [
        "Gender", "Age", "BMI", "Smoker", "Alcohol",
        "Exercise_Level", "Diet_Quality", "Sleep_Hours", "Stress_Level",
        "Father_Diabetes", "Mother_Diabetes",
        "Father_Hypertension", "Mother_Hypertension",
        "Father_HeartDisease", "Mother_HeartDisease",
        "Paternal_Grandfather_Diabetes", "Paternal_Grandmother_Diabetes",
        "Maternal_Grandfather_Diabetes", "Maternal_Grandmother_Diabetes",
        "Father_HairLoss", "Mother_HairLoss",
        "Paternal_Grandfather_HairLoss", "Maternal_Grandfather_HairLoss",
        "Father_Diabetes_Onset", "Mother_Diabetes_Onset",
        "Father_Heart_Onset", "Mother_Heart_Onset",
        "Father_Diabetes_Severity", "Mother_Diabetes_Severity",
        "Father_Heart_Severity", "Mother_Heart_Severity",
        "Paternal_Score", "Maternal_Score",
        "Family_Disease_Count", "PWIS_Diabetes", "PWIS_HeartDisease",
    ]
    with open(MODELS / "feature_columns.json", "w") as f:
        json.dump(inference_cols, f, indent=2)
    print("\n  [SAVED] models/feature_columns.json")
    print("\n[DONE] All models trained and saved to models/")
