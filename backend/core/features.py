import numpy as np
from backend.core.schemas import PredictionInput

SEVERITY_WEIGHT = {0: 0.0, 1: 0.25, 2: 0.60, 3: 1.0}


def _onset_weight(onset: int) -> float:
    if onset == 0:
        return 0.0
    if onset < 45:
        return 1.0
    if onset < 60:
        return 0.6
    return 0.3


def compute_features(p: PredictionInput) -> dict:
    """
    Compute all engineered features from raw PredictionInput.
    Returns a flat dict ready for model inference.

    PWIS formula (documented):
        PWIS = Σ [ lineage_weight × (severity_weight + onset_weight) ]
        Parent lineage_weight = 1.0 | Grandparent lineage_weight = 0.5
        severity_weight: None=0 Mild=0.25 Moderate=0.60 Severe=1.0
        onset_weight: <45yr=1.0 | 45-59yr=0.6 | ≥60yr=0.3 | none=0
    """
    # PWIS Diabetes
    pwis_d = (
        1.0 * (SEVERITY_WEIGHT[p.father_diabetes_severity] + _onset_weight(p.father_diabetes_onset))
        + 1.0 * (SEVERITY_WEIGHT[p.mother_diabetes_severity] + _onset_weight(p.mother_diabetes_onset))
        + 0.5 * SEVERITY_WEIGHT.get(p.pgf_diabetes, 0)
        + 0.5 * SEVERITY_WEIGHT.get(p.pgm_diabetes, 0)
        + 0.5 * SEVERITY_WEIGHT.get(p.mgf_diabetes, 0)
        + 0.5 * SEVERITY_WEIGHT.get(p.mgm_diabetes, 0)
    )

    # PWIS Heart
    pwis_h = (
        1.0 * (SEVERITY_WEIGHT[p.father_heart_severity] + _onset_weight(p.father_heart_onset))
        + 1.0 * (SEVERITY_WEIGHT[p.mother_heart_severity] + _onset_weight(p.mother_heart_onset))
    )

    paternal_score = (
        p.father_diabetes * 2 + p.father_hypertension * 1.5 + p.father_heart * 2
        + p.pgf_diabetes * 1 + p.pgm_diabetes * 1
    )
    maternal_score = (
        p.mother_diabetes * 2 + p.mother_hypertension * 1.5 + p.mother_heart * 2
        + p.mgf_diabetes * 1 + p.mgm_diabetes * 1
    )
    family_disease_count = (
        p.father_diabetes + p.mother_diabetes
        + p.father_hypertension + p.mother_hypertension
        + p.father_heart + p.mother_heart
        + p.pgf_diabetes + p.pgm_diabetes + p.mgf_diabetes + p.mgm_diabetes
    )

    gender_enc = 1 if p.gender.lower() == "male" else 0

    # ── Interaction features for hypertension model ───────────────────────────
    both_parents_hyp   = 1 if (p.father_hypertension and p.mother_hypertension) else 0
    high_bmi_x_fam_hyp = (1 if p.bmi > 30 else 0) * (p.father_hypertension + p.mother_hypertension)
    stress_x_fam_hyp   = p.stress_level * (p.father_hypertension + p.mother_hypertension)

    # ── Interaction features for heart model ─────────────────────────────────
    both_parents_heart = 1 if (p.father_heart and p.mother_heart) else 0
    pwis_x_smoker      = pwis_h * p.smoker
    pwis_x_high_bmi    = pwis_h * (1 if p.bmi > 30 else 0)
    early_onset_father = 1 if (p.father_heart and p.father_heart_onset > 0 and p.father_heart_onset < 50) else 0
    early_onset_mother = 1 if (p.mother_heart and p.mother_heart_onset > 0 and p.mother_heart_onset < 50) else 0
    high_risk_combined = 1 if (pwis_h > 1.0 and p.smoker) else 0

    # ── Interaction features for hair loss model ──────────────────────────────
    male_x_father_hl   = gender_enc * p.father_hair_loss
    male_x_pgf_hl      = gender_enc * p.pgf_hair_loss
    age_x_father_hl    = p.age * p.father_hair_loss
    both_grandfathers  = 1 if (p.pgf_hair_loss and p.mgf_hair_loss) else 0
    both_parents_hl    = 1 if (p.father_hair_loss and p.mother_hair_loss) else 0

    return {
        "Gender":                        gender_enc,
        "Age":                           p.age,
        "BMI":                           p.bmi,
        "HbA1c":                         5.5,
        "Blood_Glucose":                 100,
        "Smoker":                        p.smoker,
        "Alcohol":                       p.alcohol,
        "Exercise_Level":                p.exercise_level,
        "Diet_Quality":                  p.diet_quality,
        "Sleep_Hours":                   p.sleep_hours,
        "Stress_Level":                  p.stress_level,
        "Father_Diabetes":               p.father_diabetes,
        "Mother_Diabetes":               p.mother_diabetes,
        "Father_Hypertension":           p.father_hypertension,
        "Mother_Hypertension":           p.mother_hypertension,
        "Father_HeartDisease":           p.father_heart,
        "Mother_HeartDisease":           p.mother_heart,
        "Paternal_Grandfather_Diabetes": p.pgf_diabetes,
        "Paternal_Grandmother_Diabetes": p.pgm_diabetes,
        "Maternal_Grandfather_Diabetes": p.mgf_diabetes,
        "Maternal_Grandmother_Diabetes": p.mgm_diabetes,
        "Father_HairLoss":               p.father_hair_loss,
        "Mother_HairLoss":               p.mother_hair_loss,
        "Paternal_Grandfather_HairLoss": p.pgf_hair_loss,
        "Maternal_Grandfather_HairLoss": p.mgf_hair_loss,
        "Father_Diabetes_Onset":         p.father_diabetes_onset,
        "Mother_Diabetes_Onset":         p.mother_diabetes_onset,
        "Father_Heart_Onset":            p.father_heart_onset,
        "Mother_Heart_Onset":            p.mother_heart_onset,
        "Father_Diabetes_Severity":      p.father_diabetes_severity,
        "Mother_Diabetes_Severity":      p.mother_diabetes_severity,
        "Father_Heart_Severity":         p.father_heart_severity,
        "Mother_Heart_Severity":         p.mother_heart_severity,
        "Paternal_Score":                round(paternal_score, 4),
        "Maternal_Score":                round(maternal_score, 4),
        "Family_Disease_Count":          family_disease_count,
        "PWIS_Diabetes":                 round(pwis_d, 4),
        "PWIS_HeartDisease":             round(pwis_h, 4),
        # Hypertension interaction features
        "Both_Parents_Hyp":              both_parents_hyp,
        "HighBMI_x_FamHyp":             high_bmi_x_fam_hyp,
        "Stress_x_FamHyp":              stress_x_fam_hyp,
        # Heart interaction features
        "Both_Parents_Heart":            both_parents_heart,
        "PWIS_x_Smoker":                pwis_x_smoker,
        "PWIS_x_HighBMI":               pwis_x_high_bmi,
        "EarlyOnset_Father":             early_onset_father,
        "EarlyOnset_Mother":             early_onset_mother,
        "HighRisk_Combined":             high_risk_combined,
        # Hair loss interaction features
        "Male_x_FatherHL":              male_x_father_hl,
        "Male_x_PGF_HL":               male_x_pgf_hl,
        "Age_x_FatherHL":              age_x_father_hl,
        "Both_Grandfathers":            both_grandfathers,
        "Both_Parents":                 both_parents_hl,
    }
