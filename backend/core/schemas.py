from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: datetime
    class Config:
        from_attributes = True


# ── Family Member ─────────────────────────────────────────────────────────────
class FamilyMemberIn(BaseModel):
    relation: str
    gender: Optional[str] = None
    age: Optional[int] = None
    has_diabetes: int = 0
    diabetes_severity: int = 0
    diabetes_onset: int = 0
    has_hypertension: int = 0
    has_heart_disease: int = 0
    heart_severity: int = 0
    heart_onset: int = 0
    has_hair_loss: int = 0

class FamilyMemberOut(FamilyMemberIn):
    id: int
    user_id: int
    class Config:
        from_attributes = True


# ── Prediction Input ──────────────────────────────────────────────────────────
class PredictionInput(BaseModel):
    # Demographics
    gender: str
    age: int
    bmi: float
    # Lifestyle
    smoker: int
    alcohol: int
    exercise_level: int       # 0=Low 1=Moderate 2=High
    diet_quality: int         # 0=Poor 1=Average 2=Good
    sleep_hours: float
    stress_level: int         # 1-10
    # Parental flags
    father_diabetes: int
    mother_diabetes: int
    father_hypertension: int
    mother_hypertension: int
    father_heart: int
    mother_heart: int
    # Grandparent flags
    pgf_diabetes: int
    pgm_diabetes: int
    mgf_diabetes: int
    mgm_diabetes: int
    # Hair loss flags
    father_hair_loss: int
    mother_hair_loss: int
    pgf_hair_loss: int
    mgf_hair_loss: int
    # Severity (0-3)
    father_diabetes_severity: int
    mother_diabetes_severity: int
    father_heart_severity: int
    mother_heart_severity: int
    # Onset ages
    father_diabetes_onset: int
    mother_diabetes_onset: int
    father_heart_onset: int
    mother_heart_onset: int


# ── Prediction Output ─────────────────────────────────────────────────────────
class PredictionOut(BaseModel):
    diabetes_risk: float
    hypertension_risk: float
    heart_risk: float
    hair_loss_norwood: int
    onset_diabetes_years: float
    onset_heart_years: float
    pwis_diabetes: float
    pwis_heart: float
    paternal_score: float
    maternal_score: float
    family_disease_count: int
    shap_values: dict
    recommendation: str


# ── History ───────────────────────────────────────────────────────────────────
class HistoryOut(BaseModel):
    id: int
    predicted_at: datetime
    diabetes_risk: float
    hypertension_risk: float
    heart_risk: float
    hair_loss_norwood: int
    recommendation: str
    class Config:
        from_attributes = True
