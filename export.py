from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io

def generate_pdf_report(logs, summary, achievements, streak):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    elements = []

    # Title style
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=24, textColor=colors.HexColor('#7F77DD'),
                                  spaceAfter=6, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                     fontSize=11, textColor=colors.HexColor('#888780'),
                                     spaceAfter=20, alignment=TA_CENTER)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                    fontSize=14, textColor=colors.HexColor('#2C2C2A'),
                                    spaceBefore=16, spaceAfter=8)
    normal_style = ParagraphStyle('Body', parent=styles['Normal'],
                                   fontSize=10, textColor=colors.HexColor('#444441'),
                                   spaceAfter=4)

    # Header
    elements.append(Paragraph("🧠 AI Health Coach", title_style))
    elements.append(Paragraph(f"Weekly Report — Generated {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#D3D1C7')))
    elements.append(Spacer(1, 0.4*cm))

    # Streak
    if streak > 0:
        elements.append(Paragraph(f"🔥 Current Streak: {streak} days", heading_style))
        elements.append(Spacer(1, 0.2*cm))

    # Summary stats
    if summary:
        elements.append(Paragraph("📋 Weekly Summary", heading_style))
        summary_data = [
            ["Metric", "Value"],
            ["Average Mood", f"{summary['avg_mood']} / 10"],
            ["Average Sleep", f"{summary['avg_sleep']} hours"],
            ["Average Energy", f"{summary['avg_energy']} / 10"],
            ["Total Tasks Completed", str(summary['total_tasks'])],
            ["Days Logged", f"{summary['days_logged']} / 7"],
            ["Best Day", summary['best_day']],
            ["Toughest Day", summary['worst_day']],
        ]
        t = Table(summary_data, colWidths=[9*cm, 7*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7F77DD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F1EFE8'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D3D1C7')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.4*cm))

    # Daily log table
    if logs:
        elements.append(Paragraph("📓 Daily Log", heading_style))
        log_data = [["Date", "Mood", "Sleep", "Energy", "Tasks", "Notes"]]
        for log in reversed(logs):
            date, mood, sleep_hrs, energy, tasks_done, notes = log
            log_data.append([
                str(date),
                f"{mood}/10",
                f"{sleep_hrs}h",
                f"{energy}/10",
                str(tasks_done),
                (notes[:30] + "...") if notes and len(notes) > 30 else (notes or "-")
            ])
        t2 = Table(log_data, colWidths=[3*cm, 2*cm, 2*cm, 2*cm, 2*cm, 6*cm])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1D9E75')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F1EFE8'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D3D1C7')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 0.4*cm))

    # Achievements
    earned = [a for a in achievements if a['earned']]
    if earned:
        elements.append(Paragraph("🏆 Achievements Earned", heading_style))
        for a in earned:
            elements.append(Paragraph(f"{a['icon']} <b>{a['title']}</b> — {a['desc']}", normal_style))
        elements.append(Spacer(1, 0.4*cm))

    # Footer
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#D3D1C7')))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph("Generated by AI Health Coach — all data stored locally on your PC", subtitle_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
