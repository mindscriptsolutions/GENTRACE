import pandas as pd
import numpy as np
import random
import os

random.seed(42)
np.random.seed(42)

NUM_RECORDS = 10000

# ── Encodings ────────────────────────────────────────────────────────────────
SEVERITY_MAP = {"None": 0, "Mild": 1, "Moderate": 2, "Severe": 3}
EXERCISE_MAP = {"Low": 0, "Moderate": 1, "High": 2}
DIET_MAP     = {"Poor": 0, "Average": 1, "Good": 2}

def rand_severity(has_disease):
    if has_disease == 0:
        return 0
    return random.choices([1, 2, 3], weights=[0.40, 0.35, 0.25])[0]

def onset_age(has_disease):
    if has_disease == 0:
        return 0
    return random.randint(30, 70)

# Onset weight: earlier onset → stronger hereditary signal
def onset_weight(onset):
    if onset == 0:
        return 0.0
    if onset < 45:
        return 1.0   # early onset
    if onset < 60:
        return 0.6   # mid onset
    return 0.3       # late onset

# ── Phenotype-Weighted Inheritance Score (PWIS) ───────────────────────────────
# Formula (documented for IEEE):
#   PWIS = Σ [ lineage_weight × (severity_weight + onset_weight) ]
#
#   Lineage weights:
#     Parent (1st degree)      = 1.0
#     Grandparent (2nd degree) = 0.5
#
#   Severity weights: None=0, Mild=0.25, Moderate=0.60, Severe=1.0
SEVERITY_WEIGHT = {0: 0.0, 1: 0.25, 2: 0.60, 3: 1.0}

def pwis_diabetes(fd, md, pgf_d, pgm_d, mgf_d, mgm_d,
                  fd_sev, md_sev, fd_onset, md_onset):
    score = 0.0
    score += 1.0 * (SEVERITY_WEIGHT[fd_sev] + onset_weight(fd_onset))
    score += 1.0 * (SEVERITY_WEIGHT[md_sev] + onset_weight(md_onset))
    score += 0.5 * SEVERITY_WEIGHT[rand_severity(pgf_d)]
    score += 0.5 * SEVERITY_WEIGHT[rand_severity(pgm_d)]
    score += 0.5 * SEVERITY_WEIGHT[rand_severity(mgf_d)]
    score += 0.5 * SEVERITY_WEIGHT[rand_severity(mgm_d)]
    return round(score, 4)

def pwis_heart(fh, mh, fh_sev, mh_sev, fh_onset, mh_onset):
    score = 0.0
    score += 1.0 * (SEVERITY_WEIGHT[fh_sev] + onset_weight(fh_onset))
    score += 1.0 * (SEVERITY_WEIGHT[mh_sev] + onset_weight(mh_onset))
    return round(score, 4)

# ── Norwood scale for hair loss ───────────────────────────────────────────────
def norwood_stage(gender, father_hl, pgf_hl, mgf_hl, mother_hl, age):
    if gender == "Male":
        base_prob = 0.08 + father_hl * 0.35 + pgf_hl * 0.20 + mgf_hl * 0.10 + age * 0.005
    else:
        base_prob = 0.03 + mother_hl * 0.15 + age * 0.002
    base_prob = min(base_prob, 0.95)
    if random.random() > base_prob:
        return 1  # no significant loss (stage 1 = baseline)
    # weighted toward lower stages
    return random.choices([2, 3, 4, 5, 6, 7], weights=[30, 25, 20, 12, 8, 5])[0]

rows = []

for i in range(NUM_RECORDS):

    gender = random.choice(["Male", "Female"])
    age    = random.randint(18, 60)

    # ── Parental disease flags ────────────────────────────────────────────────
    father_diabetes      = np.random.binomial(1, 0.25)
    mother_diabetes      = np.random.binomial(1, 0.22)
    father_hypertension  = np.random.binomial(1, 0.30)
    mother_hypertension  = np.random.binomial(1, 0.28)
    father_heart         = np.random.binomial(1, 0.18)
    mother_heart         = np.random.binomial(1, 0.15)

    # ── Grandparent diabetes flags ────────────────────────────────────────────
    pgf_diabetes = np.random.binomial(1, 0.28)
    pgm_diabetes = np.random.binomial(1, 0.20)
    mgf_diabetes = np.random.binomial(1, 0.26)
    mgm_diabetes = np.random.binomial(1, 0.18)

    # ── Hair loss flags ───────────────────────────────────────────────────────
    father_hair_loss = np.random.binomial(1, 0.60)
    mother_hair_loss = np.random.binomial(1, 0.15)
    pgf_hair_loss    = np.random.binomial(1, 0.70)
    mgf_hair_loss    = np.random.binomial(1, 0.45)

    # ── Severity (encoded) ────────────────────────────────────────────────────
    fd_sev  = rand_severity(father_diabetes)
    md_sev  = rand_severity(mother_diabetes)
    fh_sev  = rand_severity(father_heart)
    mh_sev  = rand_severity(mother_heart)

    # ── Onset ages ────────────────────────────────────────────────────────────
    fd_onset = onset_age(father_diabetes)
    md_onset = onset_age(mother_diabetes)
    fh_onset = onset_age(father_heart)
    mh_onset = onset_age(mother_heart)

    # ── Lifestyle ─────────────────────────────────────────────────────────────
    bmi          = round(np.clip(np.random.normal(26, 4), 16, 42), 1)
    smoker       = np.random.binomial(1, 0.20)
    exercise     = random.choices(["Low", "Moderate", "High"], weights=[30, 45, 25])[0]
    exercise_enc = EXERCISE_MAP[exercise]
    alcohol      = np.random.binomial(1, 0.30)          # 1 = regular drinker
    diet         = random.choices(["Poor", "Average", "Good"], weights=[25, 45, 30])[0]
    diet_enc     = DIET_MAP[diet]
    sleep_hours  = round(np.clip(np.random.normal(6.5, 1.2), 4, 10), 1)
    stress_level = random.randint(1, 10)                # 1=low … 10=high

    # ── Derived genetic scores ────────────────────────────────────────────────
    paternal_score = (
        father_diabetes * 2 + father_hypertension * 1.5 + father_heart * 2
        + pgf_diabetes * 1 + pgm_diabetes * 1
    )
    maternal_score = (
        mother_diabetes * 2 + mother_hypertension * 1.5 + mother_heart * 2
        + mgf_diabetes * 1 + mgm_diabetes * 1
    )
    family_disease_count = (
        father_diabetes + mother_diabetes +
        father_hypertension + mother_hypertension +
        father_heart + mother_heart +
        pgf_diabetes + pgm_diabetes + mgf_diabetes + mgm_diabetes
    )

    # ── Phenotype-Weighted Inheritance Score ──────────────────────────────────
    pwis_d = pwis_diabetes(father_diabetes, mother_diabetes,
                           pgf_diabetes, pgm_diabetes, mgf_diabetes, mgm_diabetes,
                           fd_sev, md_sev, fd_onset, md_onset)
    pwis_h = pwis_heart(father_heart, mother_heart, fh_sev, mh_sev, fh_onset, mh_onset)

    # ── Correlated target probabilities ───────────────────────────────────────
    # Diabetes: driven by PWIS + BMI + lifestyle
    diabetes_risk = (
        0.04
        + pwis_d * 0.18
        + (bmi > 28) * 0.10 + (bmi > 32) * 0.08
        + smoker * 0.05
        + alcohol * 0.04
        + (diet_enc == 0) * 0.06
        + (exercise_enc == 0) * 0.05
        + (stress_level >= 7) * 0.04
    )
    target_diabetes = int(random.random() < min(diabetes_risk, 0.95))

    # Hypertension: driven by parental hypertension + BMI + stress + lifestyle
    hypertension_risk = (
        0.06
        + (father_hypertension + mother_hypertension) * 0.14
        + (bmi > 30) * 0.10
        + smoker * 0.06
        + alcohol * 0.05
        + (stress_level >= 7) * 0.07
        + (sleep_hours < 6) * 0.05
    )
    target_hypertension = int(random.random() < min(hypertension_risk, 0.95))

    # Heart disease: driven by PWIS + hypertension + lifestyle
    heart_risk = (
        0.04
        + pwis_h * 0.20
        + target_hypertension * 0.12
        + smoker * 0.09
        + alcohol * 0.06
        + (bmi > 30) * 0.07
        + (exercise_enc == 0) * 0.05
        + (diet_enc == 0) * 0.04
    )
    target_heart = int(random.random() < min(heart_risk, 0.95))

    # Hair loss: Norwood stage (1=none … 7=complete)
    norwood = norwood_stage(gender, father_hair_loss, pgf_hair_loss,
                            mgf_hair_loss, mother_hair_loss, age)

    row = {
        # ── Demographics ──────────────────────────────────────────────────────
        "Person_ID":     f"P{i+1:05d}",
        "Gender":        gender,
        "Age":           age,
        "BMI":           bmi,

        # ── Lifestyle (all numeric) ───────────────────────────────────────────
        "Smoker":        smoker,
        "Alcohol":       alcohol,
        "Exercise_Level":exercise_enc,   # 0=Low 1=Moderate 2=High
        "Diet_Quality":  diet_enc,        # 0=Poor 1=Average 2=Good
        "Sleep_Hours":   sleep_hours,
        "Stress_Level":  stress_level,

        # ── Parental disease flags ────────────────────────────────────────────
        "Father_Diabetes":     father_diabetes,
        "Mother_Diabetes":     mother_diabetes,
        "Father_Hypertension": father_hypertension,
        "Mother_Hypertension": mother_hypertension,
        "Father_HeartDisease": father_heart,
        "Mother_HeartDisease": mother_heart,

        # ── Grandparent diabetes flags ────────────────────────────────────────
        "Paternal_Grandfather_Diabetes": pgf_diabetes,
        "Paternal_Grandmother_Diabetes": pgm_diabetes,
        "Maternal_Grandfather_Diabetes": mgf_diabetes,
        "Maternal_Grandmother_Diabetes": mgm_diabetes,

        # ── Hair loss (binary flags + Norwood) ───────────────────────────────
        "Father_HairLoss":              father_hair_loss,
        "Mother_HairLoss":              mother_hair_loss,
        "Paternal_Grandfather_HairLoss":pgf_hair_loss,
        "Maternal_Grandfather_HairLoss":mgf_hair_loss,

        # ── Onset ages ────────────────────────────────────────────────────────
        "Father_Diabetes_Onset": fd_onset,
        "Mother_Diabetes_Onset": md_onset,
        "Father_Heart_Onset":    fh_onset,
        "Mother_Heart_Onset":    mh_onset,

        # ── Severity (encoded: 0=None 1=Mild 2=Moderate 3=Severe) ────────────
        "Father_Diabetes_Severity": fd_sev,
        "Mother_Diabetes_Severity": md_sev,
        "Father_Heart_Severity":    fh_sev,
        "Mother_Heart_Severity":    mh_sev,

        # ── Derived genetic features ──────────────────────────────────────────
        "Paternal_Score":       round(paternal_score, 4),
        "Maternal_Score":       round(maternal_score, 4),
        "Family_Disease_Count": family_disease_count,

        # ── Phenotype-Weighted Inheritance Score ──────────────────────────────
        # PWIS = Σ [ lineage_weight × (severity_weight + onset_weight) ]
        # Parent lineage_weight=1.0 | Grandparent lineage_weight=0.5
        # severity_weight: None=0 Mild=0.25 Moderate=0.60 Severe=1.0
        # onset_weight: <45yr=1.0 | 45-59yr=0.6 | ≥60yr=0.3 | none=0
        "PWIS_Diabetes": pwis_d,
        "PWIS_HeartDisease": pwis_h,

        # ── Targets ───────────────────────────────────────────────────────────
        "Target_Diabetes":     target_diabetes,
        "Target_Hypertension": target_hypertension,
        "Target_HeartDisease": target_heart,
        "Target_HairLoss_Norwood": norwood,   # 1=none … 7=complete baldness
    }

    rows.append(row)

df = pd.DataFrame(rows)

os.makedirs(r"D:\GENTRACE\DATASETS", exist_ok=True)
output_path = r"D:\GENTRACE\DATASETS\pedigree_dataset.csv"
df.to_csv(output_path, index=False)

print(df.head())
print("\nDataset Shape:", df.shape)
print(f"\nSaved as {output_path}")
