#!/usr/bin/env python3
"""Build a polished PDF version of the local deployment submission report."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "pdf" / "automated-deployment-pipeline-submission-report.pdf"
SCREENSHOTS = ROOT / "outputs" / "screenshots"

NAVY = colors.HexColor("#0B1F3A")
BLUE = colors.HexColor("#1677C8")
PALE_BLUE = colors.HexColor("#EAF4FC")
GREEN = colors.HexColor("#138A5B")
GRAY = colors.HexColor("#52606D")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
    canvas.line(doc.leftMargin, 0.62 * inch, letter[0] - doc.rightMargin, 0.62 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(doc.leftMargin, 0.42 * inch, "SkyBridge Network Recovery Optimizer - Submission Report")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.42 * inch, f"Page {doc.page}")
    canvas.restoreState()


def heading(text, styles):
    return Paragraph(text, styles["SectionHeading"])


def body(text, styles):
    return Paragraph(text, styles["Body"])


def evidence_image(filename, caption, styles):
    path = SCREENSHOTS / filename
    image = Image(str(path))
    max_width = 6.55 * inch
    max_height = 7.1 * inch
    ratio = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * ratio
    image.drawHeight = image.imageHeight * ratio
    return KeepTogether([image, Spacer(1, 0.08 * inch), Paragraph(caption, styles["Caption"]), Spacer(1, 0.2 * inch)])


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.8 * inch,
        title="Automated Deployment Pipeline - Submission Report",
        author="",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=23, leading=27, textColor=NAVY, alignment=TA_CENTER, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Subtitle", parent=styles["Normal"], fontName="Helvetica",
        fontSize=10.5, leading=14, textColor=GRAY, alignment=TA_CENTER, spaceAfter=14,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=14, leading=17, textColor=NAVY, spaceBefore=12, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Body", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.4, leading=13, spaceAfter=7, textColor=colors.HexColor("#263238"),
    ))
    styles.add(ParagraphStyle(
        name="Caption", parent=styles["Normal"], fontName="Helvetica-Oblique",
        fontSize=8.5, leading=11, textColor=GRAY, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="Small", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5,
        leading=11, textColor=colors.HexColor("#263238"),
    ))

    story = [
        Spacer(1, 0.18 * inch),
        Paragraph("Automated Deployment Pipeline", styles["ReportTitle"]),
        Paragraph("SkyBridge Network Recovery Optimizer", styles["Subtitle"]),
        HRFlowable(width="100%", thickness=1.2, color=BLUE, spaceAfter=13),
    ]

    metadata = Table([
        ["Student name(s)", ""],
        ["Course / section", "[Enter course and section]"],
        ["Submission date", "[Enter date]"],
        ["GitHub repository", "https://github.com/MayFairMI6/skybridge-network-recovery-optimizer"],
    ], colWidths=[1.65 * inch, 4.85 * inch])
    metadata.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PALE_BLUE),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C7D3DE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([metadata, Spacer(1, 0.12 * inch), heading("Completed requirements", styles)])
    requirements = [
        ("Git/GitHub", "Complete. The repository contains the application, Dockerfile, Jenkinsfile, Terraform configuration, Jenkins Docker setup, and documentation."),
        ("Automated CI Trigger", "Configured as SCM polling H/2 * * * *. The optional checkbox is left unchecked until a commit-triggered build is captured without using Build Now."),
        ("Jenkins (Builder)", "Complete. Jenkins checks out the repository, builds a Docker image, and runs terraform apply."),
        ("Terraform (Deployer)", "Complete. Terraform uses the kreuzwerker/docker provider and the local Docker socket to create or replace the application container."),
        ("Docker (Runtime)", "Complete. Docker Desktop hosts both Jenkins and the deployed SkyBridge application."),
    ]
    rows = [[Paragraph("Requirement", styles["Small"]), Paragraph("Verification", styles["Small"])]]
    for label, description in requirements:
        rows.append([Paragraph(f"<b>{label}</b>", styles["Small"]), Paragraph(description, styles["Small"])])
    matrix = Table(rows, colWidths=[1.75 * inch, 4.75 * inch], repeatRows=1)
    matrix.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C7D3DE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([matrix, heading("Local setup and verification", styles)])
    story.extend([
        body("The project runs locally on macOS using Docker Desktop. Jenkins runs as the local-pipeline-jenkins Docker container and is configured in a Docker-outside-of-Docker pattern: the Docker Desktop socket is mounted into Jenkins so the Jenkins Docker CLI and Terraform Docker provider can manage the host daemon.", styles),
        body("The deployed SkyBridge dashboard is a stochastic airline disruption-recovery simulation. It evaluates flight holds, cancellation/rebooking, hotel protection, recovery inventory, passenger priority, airport-pair slot pressure, weather, airspace, and volcanic-ash signals. It is a classroom prototype using synthetic network and passenger data, not a production airline system.", styles),
        body("Verification sequence: start Docker Desktop; run Docker Compose from the repository root; open Jenkins at http://localhost:8080; run the Pipeline job; confirm a successful console log; verify local-pipeline-app is deployed to port 8081; then open http://localhost:8081 and capture the running dashboard.", styles),
        heading("Captured verification evidence", styles),
        body("The following pages contain unedited screenshots captured from the local environment. They show successful Jenkins builds, Terraform deployment, Docker runtime evidence, and the deployed application.", styles),
        PageBreak(),
        heading("1. Jenkins build history", styles),
        evidence_image("jenkins-build-history.png", "Successful Jenkins build history for the SkyBridge Pipeline job.", styles),
        PageBreak(),
        heading("2. Jenkins console output", styles),
        evidence_image("jenkins-console-success.png", "Terraform created local-pipeline-app:43, published port 8081, and the pipeline finished successfully.", styles),
        PageBreak(),
        heading("3. Docker runtime", styles),
        evidence_image("docker-runtime.png", "Docker Compose starts local-pipeline-jenkins; docker ps confirms Jenkins is running on ports 8080 and 50000.", styles),
        PageBreak(),
        heading("4. Running deployed application", styles),
        evidence_image("skybridge-dashboard.png", "SkyBridge Network Recovery Optimizer running locally at http://localhost:8081.", styles),
    ])
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()
