#!/usr/bin/env python3
"""Render the markdown submission report as a PDF."""

from pathlib import Path
import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MD = ROOT / "outputs" / "submission-report.md"
OUTPUT = ROOT / "outputs" / "pdf" / "automated-deployment-pipeline-submission-report.pdf"

NAVY = colors.HexColor("#0B1F3A")
BLUE = colors.HexColor("#1677C8")
GRAY = colors.HexColor("#52606D")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
IMAGE_RE = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*$")
UL_RE = re.compile(r"^\s*[-*]\s+(.*)$")
OL_RE = re.compile(r"^\s*(\d+)\.\s+(.*)$")
HR_RE = re.compile(r"^\s*([-*_])\1{2,}\s*$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
CODE_RE = re.compile(r"`([^`]+)`")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
    canvas.line(doc.leftMargin, 0.62 * inch, letter[0] - doc.rightMargin, 0.62 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(doc.leftMargin, 0.42 * inch, "SkyBridge Network Recovery Optimizer - Submission Report")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.42 * inch, f"Page {doc.page}")
    canvas.restoreState()


def inline_markdown(text):
    text = text.rstrip().replace("  ", " ")
    if text.startswith("[x] ") or text.startswith("[X] "):
        text = f"☑ {text[4:]}"
    elif text.startswith("[ ] "):
        text = f"☐ {text[4:]}"
    escaped = html.escape(text)
    escaped = LINK_RE.sub(r"\1 (\2)", escaped)
    escaped = BOLD_RE.sub(r"<b>\1</b>", escaped)
    escaped = ITALIC_RE.sub(r"<i>\1</i>", escaped)
    escaped = CODE_RE.sub(r"<font name='Courier'>\1</font>", escaped)
    return escaped


def image_flowable(md_path, image_ref, caption, styles):
    candidate = (md_path.parent / image_ref).resolve()
    if not candidate.exists():
        candidate = (ROOT / image_ref).resolve()
    if not candidate.exists():
        return Paragraph(
            f"<b>Missing image:</b> {html.escape(image_ref)}",
            styles["Body"],
        )
    image = Image(str(candidate))
    max_width = 6.45 * inch
    max_height = 7.0 * inch
    ratio = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * ratio
    image.drawHeight = image.imageHeight * ratio
    items = [image]
    if caption.strip():
        items.extend([Spacer(1, 0.08 * inch), Paragraph(inline_markdown(caption), styles["Caption"])])
    return KeepTogether(items)


def append_paragraph(lines, story, styles):
    text = " ".join(line.strip() for line in lines if line.strip())
    if text:
        story.extend([Paragraph(inline_markdown(text), styles["Body"]), Spacer(1, 0.04 * inch)])


def render_markdown(md_path, styles):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    story = []
    paragraph_lines = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if not stripped:
            append_paragraph(paragraph_lines, story, styles)
            paragraph_lines = []
            i += 1
            continue

        heading = HEADING_RE.match(stripped)
        image = IMAGE_RE.match(stripped)
        bullet = UL_RE.match(raw)
        numbered = OL_RE.match(raw)

        if heading or image or bullet or numbered or HR_RE.match(stripped):
            append_paragraph(paragraph_lines, story, styles)
            paragraph_lines = []

        if heading:
            level = len(heading.group(1))
            text = inline_markdown(heading.group(2))
            if level == 1:
                style = styles["Heading1"]
            elif level == 2:
                style = styles["Heading2"]
            else:
                style = styles["Heading3"]
            story.extend([Paragraph(text, style), Spacer(1, 0.05 * inch)])
            i += 1
            continue

        if image:
            caption = image.group(1)
            story.extend([image_flowable(md_path, image.group(2), caption, styles), Spacer(1, 0.12 * inch)])
            i += 1
            continue

        if HR_RE.match(stripped):
            story.extend([HRFlowable(width="100%", thickness=0.8, color=BLUE), Spacer(1, 0.08 * inch)])
            i += 1
            continue

        if bullet:
            items = []
            while i < len(lines):
                next_match = UL_RE.match(lines[i])
                if not next_match:
                    break
                items.append(f"• {inline_markdown(next_match.group(1))}")
                i += 1
            for item in items:
                story.append(Paragraph(item, styles["Bullet"]))
            story.append(Spacer(1, 0.05 * inch))
            continue

        if numbered:
            items = []
            while i < len(lines):
                next_match = OL_RE.match(lines[i])
                if not next_match:
                    break
                items.append(f"{next_match.group(1)}. {inline_markdown(next_match.group(2))}")
                i += 1
            for item in items:
                story.append(Paragraph(item, styles["Bullet"]))
            story.append(Spacer(1, 0.05 * inch))
            continue

        paragraph_lines.append(raw)
        i += 1

    append_paragraph(paragraph_lines, story, styles)
    return story


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not SOURCE_MD.exists():
        raise FileNotFoundError(f"Markdown source not found: {SOURCE_MD}")
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.8 * inch,
        title="Automated Deployment Pipeline Submission Report",
        author="",
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Heading1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceBefore=8,
            spaceAfter=9,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=colors.HexColor("#102A43"),
            spaceBefore=5,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.2,
            textColor=colors.HexColor("#243B53"),
            alignment=TA_JUSTIFY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Bullet",
            parent=styles["Body"],
            leftIndent=14,
            firstLineIndent=-10,
            spaceBefore=1,
            spaceAfter=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=10.5,
            textColor=GRAY,
            alignment=TA_CENTER,
        )
    )
    story = [Spacer(1, 0.08 * inch)] + render_markdown(SOURCE_MD, styles)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()
