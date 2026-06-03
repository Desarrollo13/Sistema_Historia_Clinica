from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "manual_sistema.md"
TARGET = ROOT / "manual_sistema.pdf"


def build_story(text):
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ManualTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor("#1a7a4a"),
        spaceAfter=10,
    )
    heading = ParagraphStyle(
        "ManualHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#1b2a3b"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "ManualBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        spaceAfter=4,
    )
    mono = ParagraphStyle(
        "ManualMono",
        parent=body,
        fontName="Courier",
        fontSize=8.5,
        leftIndent=12,
        backColor=colors.HexColor("#f5f5f5"),
        borderPadding=6,
        spaceBefore=2,
        spaceAfter=6,
    )

    story = []
    in_code = False
    code_lines = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code:
                story.append(Paragraph("<br/>".join(code_lines), mono))
                story.append(Spacer(1, 0.1 * cm))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            continue

        if not line.strip():
            story.append(Spacer(1, 0.15 * cm))
            continue

        if line.startswith("# "):
            story.append(Paragraph(line[2:], title))
            continue

        if line.startswith("## "):
            story.append(Paragraph(line[3:], heading))
            continue

        if line.startswith("### "):
            story.append(Paragraph(line[4:], heading))
            continue

        if line.startswith("- "):
            content = line[2:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"- {content}", body))
            continue

        if line[:3].isdigit() and line[1:3] == '. ':
            content = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(content, body))
            continue

        content = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(content, body))

    return story


def main():
    text = SOURCE.read_text(encoding="utf-8")
    doc = SimpleDocTemplate(
        str(TARGET),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Manual del Sistema de Historia Clinica",
    )
    doc.build(build_story(text))
    print(TARGET)


if __name__ == "__main__":
    main()
