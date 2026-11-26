"""PDF report generation (reportlab)."""
import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BLUE, INK, MUTED = colors.HexColor("#2F6FDE"), colors.HexColor("#16233F"), colors.HexColor("#6B7A99")


def _t(s) -> str:  # reportlab's built-in fonts are Latin-1 only
    return escape(str(s).encode("latin-1", "replace").decode("latin-1"))


def build_pdf(analysis: dict, file_name: str, created_at: str) -> bytes:
    r, buf = analysis, io.BytesIO()
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=INK, fontSize=22, alignment=0)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=BLUE, fontSize=13, spaceBefore=12, spaceAfter=4)
    body = ParagraphStyle("b", parent=ss["BodyText"], textColor=INK, fontSize=10, leading=14)
    small = ParagraphStyle("s", parent=body, textColor=MUTED, fontSize=8.5)
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="CV Analysis Report", author="AI Smart Job Matcher")
    sc, st = r["score"], r["stats"]
    kw = r["keywords"]
    story = [Paragraph("CV Analysis Report", h1),
             Paragraph(_t(f"File: {file_name} | Analyzed: {created_at} | Target role: {r['role']}"), small), Spacer(1, 8),
             Paragraph(f"Estimated CV quality score: <b>{sc['total']}/100</b> - {_t(sc['label'])}", body),
             Paragraph(_t(sc["explanation"]), body),
             Paragraph("This is an estimated quality score based on structure, skills and keywords. It is not a guarantee of "
                       "employment or ATS acceptance.", small), Spacer(1, 6)]
    tbl = Table([["Skills found", "Strengths", "Areas to improve", f"Keyword match ({r['role']})"],
                 [st["skills_found"], st["strengths"], st["improvements"], f"{st['keywords_pct']}%"]], hAlign="LEFT")
    tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6EEFD")), ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
                             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 1), (-1, 1), 14),
                             ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D4EE")),
                             ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DCE5F8")),
                             ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [tbl, Paragraph("Score breakdown", h2)]
    story += [Paragraph(_t(f"{k}: {v['points']:.0f} / {v['max']}"), body) for k, v in sc["breakdown"].items()]
    story.append(Paragraph("Skills detected", h2))
    for cat, names in r["skills_by_category"].items():
        story.append(Paragraph(f"<b>{_t(cat)}:</b> {_t(', '.join(names))}", body))
    if not r["skills"]:
        story.append(Paragraph("No skills detected.", body))
    story.append(Paragraph(f"Comparison with {_t(r['role'])}", h2))
    story += [Paragraph(f"<b>Compatibility (skill overlap):</b> {kw['compatibility']}%", body),
              Paragraph(f"<b>Matched:</b> {_t(', '.join(kw['matched']) or '-')}", body),
              Paragraph(f"<b>Missing (core):</b> {_t(', '.join(kw['missing_required']) or '-')}", body),
              Paragraph(f"<b>Missing (nice to have):</b> {_t(', '.join(kw['missing_preferred'][:8]) or '-')}", body),
              Paragraph(f"<b>Suggested keywords:</b> {_t(', '.join(kw['suggested_keywords'][:8]) or '-')}", body)]
    for title, key in (("Strengths", "strengths"), ("Areas to improve", "improvements"), ("Recommendations", "recommendations")):
        story.append(Paragraph(title, h2))
        story += [Paragraph("- " + _t(x), body) for x in r[key]] or [Paragraph("-", body)]
    doc.build(story)
    return buf.getvalue()
