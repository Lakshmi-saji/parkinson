import os
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_medical_report(prediction, features, patient_data):
    """
    ParkiSense Formal Clinical Report Generator.
    Hospital-grade, professional layout.
    """

    def get_val(obj, key, default=0.0):
        if hasattr(obj, key): return getattr(obj, key) or default
        if isinstance(obj, dict): return obj.get(key, default)
        return default

    pred_id   = get_val(prediction, 'id', '000')
    prob      = get_val(prediction, 'parkinson_probability', 0.0)
    risk      = get_val(prediction, 'risk_level', 'Healthy')
    if risk in ["Low", "Medium", "High"]:
        risk = f"{risk} Risk"
    conf      = get_val(prediction, 'confidence_score', 0.0)
    jitter    = get_val(features, 'mdvp_jitter_pct', 0.0) if features else 0.0
    shimmer   = get_val(features, 'mdvp_shimmer', 0.0) if features else 0.0
    hnr       = get_val(features, 'hnr', 0.0) if features else 0.0
    mdvp_fo   = get_val(features, 'mdvp_fo', 0.0) if features else 0.0

    now = datetime.datetime.now()
    report_date = now.strftime('%d %B %Y')
    report_time = now.strftime('%I:%M %p')

    # ── Colour Palette ──
    DARK_BLUE   = colors.HexColor("#0B1F3A")
    MID_BLUE    = colors.HexColor("#1A3A5C")
    ACCENT      = colors.HexColor("#1D72B8")
    LIGHT_GRAY  = colors.HexColor("#F4F7FB")
    MID_GRAY    = colors.HexColor("#7D8BA1")
    WHITE       = colors.white
    BLACK       = colors.HexColor("#0D0D0D")

    RISK_COLORS = {
        "Healthy":     colors.HexColor("#1A7A4A"),
        "Low Risk":    colors.HexColor("#2E7D32"),
        "Medium Risk": colors.HexColor("#E65100"),
        "High Risk":   colors.HexColor("#B71C1C"),
    }
    risk_color = RISK_COLORS.get(risk, ACCENT)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()

    # ── Custom Style Library ──
    def S(name, parent='Normal', **kw):
        return ParagraphStyle(name, parent=styles[parent], **kw)

    sTitle      = S('sTitle',      fontSize=22, textColor=WHITE,    leading=26, alignment=TA_CENTER, fontName='Helvetica-Bold')
    sSubtitle   = S('sSubtitle',   fontSize=9,  textColor=colors.HexColor("#A8C4E0"), alignment=TA_CENTER)
    sSectionHdr = S('sSectionHdr', fontSize=10, textColor=ACCENT,   fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=4)
    sBody       = S('sBody',       fontSize=9,  textColor=BLACK,     leading=14)
    sSmall      = S('sSmall',      fontSize=7.5, textColor=MID_GRAY, leading=11)
    sLabel      = S('sLabel',      fontSize=8,  textColor=MID_GRAY,  fontName='Helvetica-Bold')
    sValue      = S('sValue',      fontSize=9,  textColor=BLACK,     fontName='Helvetica-Bold')
    sBioLabel   = S('sBioLabel',   fontSize=8,  textColor=MID_GRAY)
    sBioValue   = S('sBioValue',   fontSize=10, textColor=BLACK,     fontName='Helvetica-Bold')
    sRiskText   = S('sRiskText',   fontSize=18, textColor=risk_color, fontName='Helvetica-Bold', alignment=TA_CENTER)
    sProbText   = S('sProbText',   fontSize=13, textColor=BLACK,     fontName='Helvetica-Bold', alignment=TA_CENTER)
    sDisclaim   = S('sDisclaim',   fontSize=7,  textColor=MID_GRAY,  leading=10)
    sSympLabel  = S('sSympLabel',  fontSize=8,  textColor=MID_GRAY,  fontName='Helvetica-Bold')
    sSympValue  = S('sSympValue',  fontSize=8,  textColor=BLACK,     leading=13)

    elements = []

    # ══════════════════════════════════════════════════
    # 1. HEADER BANNER
    # ══════════════════════════════════════════════════
    header_data = [[
        Paragraph("ParkiSense", sTitle),
        Paragraph("CLINICAL VOICE SCREENING REPORT", sSubtitle)
    ]]
    header_table = Table(header_data, colWidths=[doc.width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), DARK_BLUE),
        ('TOPPADDING',    (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING',   (0,0), (-1,-1), 18),
        ('RIGHTPADDING',  (0,0), (-1,-1), 18),
        ('SPAN',          (0,0), (-1,-1)),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('ROUNDEDCORNERS',[4]),
    ]))
    # Use two rows for title + subtitle
    header_block = [
        [Paragraph("ParkiSense", sTitle)],
        [Paragraph("CLINICAL VOICE SCREENING REPORT", sSubtitle)],
    ]
    hdr = Table(header_block, colWidths=[doc.width])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), DARK_BLUE),
        ('TOPPADDING',    (0,0), (0,0),  14),
        ('BOTTOMPADDING', (0,1), (0,1),  12),
        ('LEFTPADDING',   (0,0), (-1,-1), 20),
        ('RIGHTPADDING',  (0,0), (-1,-1), 20),
    ]))
    elements.append(hdr)
    elements.append(Spacer(1, 5*mm))

    # ── Report Meta Row ──
    meta_data = [[
        Paragraph(f"<b>Report ID:</b>  PKS-{pred_id:04d}", sBody),
        Paragraph(f"<b>Date:</b>  {report_date}", sBody),
        Paragraph(f"<b>Time:</b>  {report_time}", sBody),
        Paragraph(f"<b>Model:</b>  V65 Neural CNN", sBody),
    ]]
    meta_table = Table(meta_data, colWidths=[doc.width/4]*4)
    meta_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), LIGHT_GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('LINEBELOW',     (0,0), (-1,-1), 0.5, colors.HexColor("#DDEAF5")),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 5*mm))

    # ══════════════════════════════════════════════════
    # 2. PATIENT CLINICAL PROFILE
    # ══════════════════════════════════════════════════
    elements.append(Paragraph("PATIENT CLINICAL PROFILE", sSectionHdr))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=4))

    age_val    = patient_data.get('age', 'N/A')
    gender_val = patient_data.get('gender', 'N/A')
    profile_data = [
        [
            Paragraph("Age", sLabel),
            Paragraph("Gender", sLabel),
            Paragraph("Assessment Type", sLabel),
            Paragraph("Report Status", sLabel),
        ],
        [
            Paragraph(str(age_val), sValue),
            Paragraph(str(gender_val), sValue),
            Paragraph("Voice Biomarker Analysis", sValue),
            Paragraph("Preliminary Screening", sValue),
        ],
    ]
    profile_table = Table(profile_data, colWidths=[doc.width/4]*4)
    profile_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), LIGHT_GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('BOX',           (0,0), (-1,-1), 0.5, colors.HexColor("#D0DFF0")),
        ('INNERGRID',     (0,0), (-1,-1), 0.3, colors.HexColor("#E0EBF5")),
    ]))
    elements.append(profile_table)
    elements.append(Spacer(1, 5*mm))

    # ══════════════════════════════════════════════════
    # 3. SYMPTOMATIC CLINICAL HISTORY
    # ══════════════════════════════════════════════════
    elements.append(Paragraph("SYMPTOMATIC CLINICAL HISTORY", sSectionHdr))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=4))

    symptoms = patient_data.get('symptoms', {})
    symp_rows = []
    items = list(symptoms.items())
    for i in range(0, len(items), 2):
        left_label  = items[i][0]
        left_value  = str(items[i][1]) if items[i][1] else "Not reported"
        right_label = items[i+1][0] if i+1 < len(items) else ""
        right_value = str(items[i+1][1]) if i+1 < len(items) and items[i+1][1] else "Not reported"
        symp_rows.append([
            Paragraph(left_label, sSympLabel),
            Paragraph(left_value, sSympValue),
            Paragraph(right_label, sSympLabel),
            Paragraph(right_value, sSympValue),
        ])

    if symp_rows:
        symp_table = Table(symp_rows, colWidths=[30*mm, 65*mm, 30*mm, 45*mm])
        symp_table.setStyle(TableStyle([
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_GRAY, WHITE]),
            ('BOX',           (0,0), (-1,-1), 0.5, colors.HexColor("#D0DFF0")),
            ('LINEAFTER',     (1,0), (1,-1), 0.4, colors.HexColor("#D0DFF0")),
        ]))
        elements.append(symp_table)

    # Additional difficulties
    additional = patient_data.get('additional', '')
    if additional and additional.strip() and additional != 'No additional difficulties reported':
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("Additional Patient Reported Difficulties", sSympLabel))
        add_table = Table([[Paragraph(additional, sBody)]], colWidths=[doc.width])
        add_table.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), LIGHT_GRAY),
            ('TOPPADDING',    (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ('BOX',           (0,0), (-1,-1), 0.5, colors.HexColor("#D0DFF0")),
        ]))
        elements.append(add_table)

    elements.append(Spacer(1, 5*mm))

    # ══════════════════════════════════════════════════
    # 4. VOICE BIOMARKER ANALYSIS
    # ══════════════════════════════════════════════════
    elements.append(Paragraph("VOICE BIOMARKER ANALYSIS", sSectionHdr))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=4))

    bio_rows = [
        [
            Paragraph("Biomarker", sSympLabel),
            Paragraph("Measured Value", sSympLabel),
            Paragraph("Reference Range", sSympLabel),
            Paragraph("Status", sSympLabel),
        ],
        [
            Paragraph("Fundamental Frequency (F0)", sBody),
            Paragraph(f"{mdvp_fo:.2f} Hz", sValue),
            Paragraph("85 – 255 Hz", sBody),
            Paragraph("Within Normal Range" if 85 <= mdvp_fo <= 255 else "Outside Normal Range", sBody),
        ],
        [
            Paragraph("Vocal Jitter (Pitch Instability)", sBody),
            Paragraph(f"{jitter:.4f} %", sValue),
            Paragraph("< 1.04 %", sBody),
            Paragraph("Normal" if jitter < 1.04 else "Elevated", sBody),
        ],
        [
            Paragraph("Vocal Shimmer (Amplitude Instability)", sBody),
            Paragraph(f"{shimmer:.4f}", sValue),
            Paragraph("< 0.167", sBody),
            Paragraph("Normal" if shimmer < 0.167 else "Elevated", sBody),
        ],
        [
            Paragraph("Harmonics-to-Noise Ratio (HNR)", sBody),
            Paragraph(f"{hnr:.2f} dB", sValue),
            Paragraph("> 20.0 dB", sBody),
            Paragraph("Normal" if hnr >= 20.0 else "Reduced", sBody),
        ],
    ]

    bio_table = Table(bio_rows, colWidths=[65*mm, 35*mm, 40*mm, 30*mm])
    bio_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), MID_BLUE),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_GRAY, WHITE]),
        ('BOX',           (0,0), (-1,-1), 0.5, colors.HexColor("#D0DFF0")),
        ('INNERGRID',     (0,0), (-1,-1), 0.3, colors.HexColor("#E0EBF5")),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 8),
    ]))
    elements.append(bio_table)
    elements.append(Spacer(1, 5*mm))

    # ══════════════════════════════════════════════════
    # 5. DIAGNOSTIC CONCLUSION
    # ══════════════════════════════════════════════════
    elements.append(Paragraph("DIAGNOSTIC CONCLUSION", sSectionHdr))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=4))

    score_pct = prob * 100
    conf_pct  = conf * 100

    conclusion_data = [
        [
            Table([
                [Paragraph("Parkinson's Probability Score", sLabel)],
                [Paragraph(f"{score_pct:.1f}%", sProbText)],
            ]),
            Table([
                [Paragraph("Risk Classification", sLabel)],
                [Paragraph(risk, sRiskText)],
            ]),
            Table([
                [Paragraph("Diagnostic Confidence", sLabel)],
                [Paragraph(f"{conf_pct:.1f}%", sProbText)],
            ]),
        ]
    ]
    conc_table = Table(conclusion_data, colWidths=[doc.width/3]*3)
    conc_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), LIGHT_GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('BOX',           (0,0), (-1,-1), 1.2, ACCENT),
        ('LINEAFTER',     (0,0), (1,-1), 0.5, colors.HexColor("#D0DFF0")),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(conc_table)
    elements.append(Spacer(1, 6*mm))

    # ── Clinical Interpretation ──
    interp_map = {
        "Healthy":     "Voice biomarker analysis indicates no significant neurological abnormalities. Vocal acoustic patterns are within the expected healthy range. Routine monitoring is advised.",
        "Low Risk":    "Minor deviations detected in vocal biomarkers. Clinical correlation is recommended. A follow-up assessment within 6 months is suggested.",
        "Medium Risk": "Moderate acoustic anomalies detected consistent with early-stage neurological involvement. Clinical referral to a Neurologist is strongly recommended.",
        "High Risk":   "Significant vocal biomarker deviations detected. Findings are strongly indicative of neurological dysregulation. Urgent referral for comprehensive UPDRS evaluation is advised.",
    }
    interp = interp_map.get(risk, "Refer to a specialist for further evaluation.")
    interp_table = Table([[Paragraph(f"<b>Clinical Interpretation:</b> {interp}", sBody)]], colWidths=[doc.width])
    interp_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor("#EAF4FF")),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 12),
        ('BOX',           (0,0), (-1,-1), 0.5, ACCENT),
        ('LINEBEFORE',    (0,0), (0,-1), 3, ACCENT),
    ]))
    elements.append(interp_table)
    elements.append(Spacer(1, 6*mm))

    # ══════════════════════════════════════════════════
    # 6. FOOTER — DISCLAIMER
    # ══════════════════════════════════════════════════
    elements.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=4))
    disclaimer = (
        "<b>DISCLAIMER:</b> This report is generated by ParkiSense, an AI-assisted clinical voice screening system. "
        "It is intended solely as a preliminary screening aid and does NOT constitute a definitive medical diagnosis. "
        "Results must be reviewed and interpreted by a qualified Neurologist in conjunction with a full clinical "
        "examination, including the Unified Parkinson's Disease Rating Scale (UPDRS). "
        "ParkiSense accepts no liability for clinical decisions made solely on the basis of this report."
    )
    elements.append(Paragraph(disclaimer, sDisclaim))
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph(
        f"Generated by ParkiSense Clinical Engine V65 Neural CNN  |  Report ID: PKS-{pred_id:04d}  |  {report_date}",
        ParagraphStyle('footer2', parent=styles['Normal'], fontSize=7, textColor=MID_GRAY, alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
