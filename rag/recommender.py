"""
RAG Recommendation Engine
─────────────────────────
Retrieves relevant medical guidance from the local knowledge base
and generates a personalised precautionary recommendation.

Knowledge base files live in rag/knowledge_base/*.txt
Each file is one topic (diabetes, hypertension, heart, hair_loss).
"""

from pathlib import Path
import re

KB_DIR = Path("rag/knowledge_base")


def _load_kb(topic: str) -> str:
    path = KB_DIR / f"{topic}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _risk_label(risk: float) -> str:
    if risk < 0.30: return "low"
    if risk < 0.60: return "moderate"
    return "high"


def get_recommendation(
    diabetes_risk: float,
    hypertension_risk: float,
    heart_risk: float,
    hair_norwood: int,
    features: dict,
) -> str:
    """
    Retrieves relevant passages from the knowledge base for each
    elevated-risk disease and assembles a personalised recommendation.
    """
    lines = ["=== GeneTrace Personalised Precautionary Recommendations ===\n"]

    # ── Diabetes ──────────────────────────────────────────────────────────────
    d_label = _risk_label(diabetes_risk)
    lines.append(f"[Diabetes Risk: {diabetes_risk*100:.1f}% — {d_label.upper()}]")
    if d_label in ("moderate", "high"):
        kb = _load_kb("diabetes")
        lines.append(_retrieve(kb, ["diet", "exercise", "blood glucose", "prevention"]))
    else:
        lines.append("Your hereditary diabetes risk is currently low. Maintain a balanced diet and regular activity.")
    lines.append("")

    # ── Hypertension ─────────────────────────────────────────────────────────
    h_label = _risk_label(hypertension_risk)
    lines.append(f"[Hypertension Risk: {hypertension_risk*100:.1f}% — {h_label.upper()}]")
    if h_label in ("moderate", "high"):
        kb = _load_kb("hypertension")
        lines.append(_retrieve(kb, ["sodium", "blood pressure", "stress", "lifestyle"]))
    else:
        lines.append("Your hereditary hypertension risk is currently low. Monitor blood pressure annually.")
    lines.append("")

    # ── Heart Disease ─────────────────────────────────────────────────────────
    c_label = _risk_label(heart_risk)
    lines.append(f"[Cardiovascular Risk: {heart_risk*100:.1f}% — {c_label.upper()}]")
    if c_label in ("moderate", "high"):
        kb = _load_kb("heart")
        lines.append(_retrieve(kb, ["cholesterol", "exercise", "smoking", "cardiac"]))
    else:
        lines.append("Your hereditary cardiovascular risk is currently low. Avoid smoking and stay active.")
    lines.append("")

    # ── Hair Loss ─────────────────────────────────────────────────────────────
    lines.append(f"[Hair Loss: Norwood Stage {hair_norwood}]")
    if hair_norwood >= 3:
        kb = _load_kb("hair_loss")
        lines.append(_retrieve(kb, ["androgenetic", "treatment", "DHT", "prevention"]))
    else:
        lines.append("No significant hereditary hair loss risk detected at this stage.")
    lines.append("")

    # ── Lifestyle-specific additions ──────────────────────────────────────────
    if features.get("Smoker", 0):
        lines.append("⚠ Smoking significantly amplifies your hereditary cardiovascular and diabetes risk. "
                     "Consult a cessation programme (WHO MPOWER guidelines).")
    if features.get("BMI", 0) > 30:
        lines.append("⚠ BMI > 30 is a strong modifiable risk factor. "
                     "A 5–10% weight reduction can substantially lower diabetes and hypertension risk (NIH).")
    if features.get("Stress_Level", 0) >= 7:
        lines.append("⚠ High stress level detected. Chronic stress elevates cortisol, "
                     "increasing hypertension and cardiovascular risk. Consider mindfulness or CBT.")
    if features.get("Sleep_Hours", 8) < 6:
        lines.append("⚠ Sleep < 6 hours is associated with increased hypertension and metabolic risk (CDC). "
                     "Target 7–9 hours per night.")

    lines.append("\nDisclaimer: These recommendations are based on hereditary risk estimates only "
                 "and do not constitute medical diagnosis. Consult a qualified healthcare professional.")

    return "\n".join(lines)


def _retrieve(kb_text: str, keywords: list, max_sentences: int = 4) -> str:
    """Simple keyword-based retrieval from knowledge base text."""
    if not kb_text:
        return "  • Consult your physician for personalised guidance based on your family history."

    sentences = re.split(r'(?<=[.!?])\s+', kb_text)
    scored = []
    for s in sentences:
        score = sum(1 for kw in keywords if kw.lower() in s.lower())
        if score > 0:
            scored.append((score, s.strip()))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [s for _, s in scored[:max_sentences]]
    if not top:
        return "  • Follow evidence-based guidelines from your healthcare provider."
    return "\n".join(f"  • {s}" for s in top)
