import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from io import BytesIO

from backend.database import get_db, PredictionHistory, User
from backend.core.schemas import HistoryOut
from backend.core.security import get_current_user, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/history", tags=["History"])


def _get_user_by_token(token: str, db: Session) -> User:
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/", response_model=List[HistoryOut])
def get_history(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == current_user.id)
        .order_by(PredictionHistory.predicted_at.desc())
        .all()
    )


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    record = db.query(PredictionHistory).filter(
        PredictionHistory.id == record_id,
        PredictionHistory.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()


@router.get("/{record_id}/report")
def download_report(record_id: int,
                    token: Optional[str] = Query(None),
                    db: Session = Depends(get_db)):
    # Resolve user from query param token (window.open can't send headers)
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    current_user = _get_user_by_token(token, db)

    record = db.query(PredictionHistory).filter(
        PredictionHistory.id == record_id,
        PredictionHistory.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                topMargin=2*cm, bottomMargin=2*cm,
                                leftMargin=2*cm, rightMargin=2*cm)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle("GT_Title", parent=styles["Title"],
                                     textColor=colors.HexColor("#1a3c5e"),
                                     fontSize=20, spaceAfter=6)
        h2_style    = ParagraphStyle("GT_H2", parent=styles["Heading2"],
                                     textColor=colors.HexColor("#1a3c5e"),
                                     fontSize=13, spaceBefore=12, spaceAfter=4)
        normal      = styles["Normal"]
        italic      = styles["Italic"]

        def risk_color(risk):
            if risk < 0.30: return colors.HexColor("#2a9d8f")
            if risk < 0.60: return colors.HexColor("#f4a261")
            return colors.HexColor("#e63946")

        def risk_label(risk):
            if risk < 0.30: return "Low"
            if risk < 0.60: return "Moderate"
            return "High"

        def norwood_label(s):
            m = {1:"Minimal",2:"Early",3:"Moderate",4:"Significant",5:"Advanced",6:"Severe",7:"Complete"}
            return m.get(s, "Unknown")

        story = []

        # Header
        story.append(Paragraph("GeneTrace", title_style))
        story.append(Paragraph("Hereditary Disease Risk Assessment Report", styles["Heading3"]))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3c5e")))
        story.append(Spacer(1, 0.4*cm))

        # Patient info
        story.append(Paragraph("Patient Information", h2_style))
        info_data = [
            ["Patient Name", current_user.full_name],
            ["Email",        current_user.email],
            ["Report Date",  record.predicted_at.strftime("%Y-%m-%d %H:%M UTC")],
            ["Report ID",    f"GT-{record.id:06d}"],
        ]
        info_table = Table(info_data, colWidths=[5*cm, 11*cm])
        info_table.setStyle(TableStyle([
            ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE",  (0,0), (-1,-1), 10),
            ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#f0f4f8"), colors.white]),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
            ("PADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.5*cm))

        # Risk Summary
        story.append(Paragraph("Hereditary Risk Summary", h2_style))
        risk_data = [
            ["Disease", "Risk Score", "Risk Level", "Status"],
            ["Type 2 Diabetes",
             f"{record.diabetes_risk*100:.1f}%",
             risk_label(record.diabetes_risk),
             "Elevated" if record.diabetes_risk >= 0.30 else "Normal Range"],
            ["Hypertension",
             f"{record.hypertension_risk*100:.1f}%",
             risk_label(record.hypertension_risk),
             "Elevated" if record.hypertension_risk >= 0.30 else "Normal Range"],
            ["Cardiovascular Disease",
             f"{record.heart_risk*100:.1f}%",
             risk_label(record.heart_risk),
             "Elevated" if record.heart_risk >= 0.30 else "Normal Range"],
            ["Androgenetic Alopecia",
             f"Stage {record.hair_loss_norwood}/7",
             norwood_label(record.hair_loss_norwood),
             "Hereditary Pattern Detected" if record.hair_loss_norwood >= 3 else "Minimal Risk"],
        ]
        risk_table = Table(risk_data, colWidths=[5.5*cm, 3*cm, 3.5*cm, 4*cm])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#1a3c5e")),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
            ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#e2e8f0")),
            ("ALIGN",       (1,0), (-1,-1), "CENTER"),
            ("PADDING",     (0,0), (-1,-1), 7),
            ("TEXTCOLOR",   (2,1), (2,1), risk_color(record.diabetes_risk)),
            ("TEXTCOLOR",   (2,2), (2,2), risk_color(record.hypertension_risk)),
            ("TEXTCOLOR",   (2,3), (2,3), risk_color(record.heart_risk)),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.5*cm))

        # Onset Estimates
        story.append(Paragraph("Estimated Age of Onset", h2_style))
        onset_data = [
            ["Disease", "Estimated Onset Age", "Basis"],
            ["Type 2 Diabetes",
             f"{record.onset_diabetes:.0f} years" if record.onset_diabetes and record.onset_diabetes > 0 else "N/A",
             "Pedigree regression model"],
            ["Cardiovascular Disease",
             f"{record.onset_heart:.0f} years" if record.onset_heart and record.onset_heart > 0 else "N/A",
             "Pedigree regression model"],
        ]
        onset_table = Table(onset_data, colWidths=[5.5*cm, 4*cm, 6.5*cm])
        onset_table.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#2563a8")),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
            ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#e2e8f0")),
            ("ALIGN",       (1,0), (1,-1), "CENTER"),
            ("PADDING",     (0,0), (-1,-1), 7),
        ]))
        story.append(onset_table)
        story.append(Spacer(1, 0.5*cm))

        # SHAP
        if record.shap_json:
            try:
                shap_vals = json.loads(record.shap_json)
                if shap_vals:
                    story.append(Paragraph("Top Contributing Features (SHAP Analysis)", h2_style))
                    story.append(Paragraph(
                        "The following features had the greatest influence on the diabetes risk prediction:",
                        normal))
                    story.append(Spacer(1, 0.2*cm))
                    shap_data = [["Feature", "SHAP Value", "Direction"]]
                    for feat, val in list(shap_vals.items())[:8]:
                        label = feat.replace("_", " ")
                        direction = "Increases Risk" if val >= 0 else "Decreases Risk"
                        shap_data.append([label, f"{val:+.4f}", direction])
                    shap_table = Table(shap_data, colWidths=[8*cm, 3.5*cm, 4.5*cm])
                    shap_table.setStyle(TableStyle([
                        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#06d6a0")),
                        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
                        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
                        ("FONTSIZE",    (0,0), (-1,-1), 9),
                        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
                        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#e2e8f0")),
                        ("ALIGN",       (1,0), (-1,-1), "CENTER"),
                        ("PADDING",     (0,0), (-1,-1), 6),
                    ]))
                    story.append(shap_table)
                    story.append(Spacer(1, 0.5*cm))
            except Exception:
                pass

        # Recommendations
        story.append(Paragraph("Personalized Preventive Recommendations", h2_style))
        story.append(Paragraph(
            "The following recommendations are retrieved from WHO, NIH, and CDC knowledge bases "
            "based on your hereditary risk profile:", normal))
        story.append(Spacer(1, 0.3*cm))
        if record.recommendation:
            for line in record.recommendation.split("\n"):
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 0.15*cm))
                elif line.startswith("==="):
                    story.append(Paragraph(line.replace("=","").strip(), h2_style))
                elif line.startswith("[") and line.endswith("]"):
                    story.append(Paragraph(f"<b>{line}</b>", normal))
                elif line.startswith("•"):
                    story.append(Paragraph(f"&nbsp;&nbsp;{line}", normal))
                else:
                    story.append(Paragraph(line, normal))

        story.append(Spacer(1, 0.8*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            "<b>Disclaimer:</b> GeneTrace provides hereditary risk estimates only based on family "
            "pedigree analysis. This report does not constitute a medical diagnosis. Predictions are "
            "probabilistic estimates and should not replace professional medical advice. Always consult "
            "a qualified healthcare professional for diagnosis and treatment.",
            italic))

        doc.build(story)
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=GeneTrace_Report_{record_id}.pdf"}
        )

    except ImportError:
        raise HTTPException(status_code=500, detail="reportlab not installed. Run: pip install reportlab")


def _level(risk: float) -> str:
    if risk < 0.30: return "Low"
    if risk < 0.60: return "Moderate"
    return "High"
