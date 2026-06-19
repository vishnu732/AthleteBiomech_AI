from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def get_risk_color(risk_level):
    if risk_level == "HIGH":
        return colors.red
    elif risk_level == "MEDIUM":
        return colors.orange
    return colors.green


def add_bullet_list(story, items, style):
    if not items:
        story.append(Paragraph("- No major items detected.", style))
        return

    for item in items:
        story.append(Paragraph(f"- {item}", style))


def create_coach_pdf_report(
    athlete_name,
    sport,
    workload_result,
    pose_result,
    combined_score,
    combined_level
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=16
    )

    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#111827"),
        spaceBefore=14,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#374151")
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6B7280")
    )

    story = []

    report_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    workload_score = workload_result.get("risk_score", "N/A")
    workload_level = workload_result.get("risk_level", "N/A")

    movement_score = pose_result.get("movement_risk_score", "N/A")
    movement_level = pose_result.get("movement_risk_level", "N/A")

    risky_areas = workload_result.get("risky_areas", [])
    workload_reasons = workload_result.get("reasons", [])
    movement_flags = pose_result.get("risk_flags", [])
    average_angles = pose_result.get("average_angles", {})

    story.append(Paragraph("AthleteBiomech AI - Coach Injury Risk Report", title_style))
    story.append(Paragraph(f"Generated: {report_date}", small_style))
    story.append(Spacer(1, 12))

    athlete_table = Table(
        [
            ["Athlete Name", athlete_name],
            ["Sport", sport],
            ["Combined Risk Level", combined_level],
            ["Combined Risk Score", f"{combined_score}%"]
        ],
        colWidths=[2.2 * inch, 4.5 * inch]
    )

    athlete_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E5E7EB")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 8)
            ]
        )
    )

    story.append(athlete_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Risk Score Summary", section_style))

    score_table = Table(
        [
            ["Risk Type", "Score", "Level"],
            ["Workload Risk", f"{workload_score}%", workload_level],
            ["Movement Risk", f"{movement_score}%", movement_level],
            ["Combined Risk", f"{combined_score}%", combined_level]
        ],
        colWidths=[2.2 * inch, 1.5 * inch, 2.0 * inch]
    )

    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9FAFB"))
            ]
        )
    )

    story.append(score_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Sport-Specific Risky Body Areas", section_style))
    add_bullet_list(story, risky_areas, normal_style)

    story.append(Paragraph("Workload Risk Reasons", section_style))
    add_bullet_list(story, workload_reasons, normal_style)

    story.append(Paragraph("Video Movement Risk Flags", section_style))
    add_bullet_list(story, movement_flags, normal_style)

    story.append(Paragraph("Average Joint Angles", section_style))

    if average_angles:
        angle_rows = [["Metric", "Average Angle"]]
        for metric, value in average_angles.items():
            angle_rows.append([metric, f"{value} degrees"])

        angle_table = Table(
            angle_rows,
            colWidths=[3.8 * inch, 2.0 * inch]
        )

        angle_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 7)
                ]
            )
        )

        story.append(angle_table)
    else:
        story.append(Paragraph("- No joint-angle data available.", normal_style))

    story.append(Paragraph("Coach Recommendations", section_style))

    if combined_level == "HIGH":
        recommendations = [
            "Reduce training load temporarily.",
            "Increase recovery and rest days.",
            "Review movement technique with a coach.",
            "Add mobility, stability, and strengthening exercises.",
            "Monitor pain, fatigue, or discomfort after sessions.",
            "Consider physiotherapist review if pain is present."
        ]
    elif combined_level == "MEDIUM":
        recommendations = [
            "Maintain balanced workload and recovery.",
            "Avoid sudden increase in training volume.",
            "Add proper warm-up and cooldown.",
            "Track weekly workload and movement changes.",
            "Focus on technique correction for flagged movement risks."
        ]
    else:
        recommendations = [
            "Current risk appears manageable.",
            "Continue tracking workload weekly.",
            "Maintain strength, mobility, and recovery habits.",
            "Recheck movement analysis periodically."
        ]

    add_bullet_list(story, recommendations, normal_style)

    story.append(Spacer(1, 16))

    disclaimer = (
        "Disclaimer: This report is generated by an AI sports analytics prototype. "
        "It is intended for educational and performance-analysis purposes only. "
        "It should not be used as a medical diagnosis."
    )

    story.append(Paragraph(disclaimer, small_style))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes