"""Generate sample company PDF for NexaData Solutions."""
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def create_nexadata_pdf():
    output_dir = Path(__file__).resolve().parent.parent / "company_docs"
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "NexaData_Company_Overview_and_Services.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "NexaTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=0
    )

    subtitle_style = ParagraphStyle(
        "NexaSub",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0D9488")
    )

    h1_style = ParagraphStyle(
        "NexaH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "NexaBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155")
    )

    bullet_style = ParagraphStyle(
        "NexaBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        leftIndent=15
    )

    story = []

    # Title & Header
    story.append(Paragraph("NexaData Solutions", title_style))
    story.append(Paragraph("Ask. Analyze. Discover. — Autonomous AI Data Analytics & Enterprise Intelligence", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceAfter=15))

    # Section 1: About
    story.append(Paragraph("1. About NexaData Solutions", h1_style))
    story.append(Paragraph(
        "NexaData Solutions is an advanced autonomous data intelligence and AI analytics platform. We bridge complex relational databases, unstructured documents, and business intelligence dashboards through natural language conversational AI. Our mission is to democratize instant, accurate data discovery for non-technical users and enterprise decision-makers.",
        body_style
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Core Platform Pillars:</b>", body_style))
    story.append(Paragraph("• <b>Ask:</b> Natural language conversational interface allowing users to query data in plain English.", bullet_style))
    story.append(Paragraph("• <b>Analyze:</b> Ultra-fast in-memory DuckDB query execution processing 50,000+ records in ~30 milliseconds.", bullet_style))
    story.append(Paragraph("• <b>Discover:</b> Autonomous exploratory data analysis, dynamic Plotly visualizations, and executive PDF reporting.", bullet_style))

    # Section 2: Services
    story.append(Paragraph("2. Enterprise Solutions & Pricing Plans", h1_style))
    story.append(Paragraph("NexaData offers scalable tiers for teams of all sizes:", body_style))
    story.append(Spacer(1, 6))

    services_data = [
        [Paragraph("<b>Tier</b>", body_style), Paragraph("<b>Features Included</b>", body_style), Paragraph("<b>Pricing</b>", body_style)],
        [
            Paragraph("<b>Starter Intelligence Plan</b>", body_style),
            Paragraph("Up to 5 CSV/Excel datasets, standard AI querying, interactive chart exports, and community support.", body_style),
            Paragraph("$49 / month", body_style)
        ],
        [
            Paragraph("<b>Professional Analytics Plan</b>", body_style),
            Paragraph("Unlimited datasets, live SQL database connectors, executive PDF generator, and sub-millisecond document RAG.", body_style),
            Paragraph("$149 / month", body_style)
        ],
        [
            Paragraph("<b>Enterprise Dedicated Instance</b>", body_style),
            Paragraph("Custom private cloud deployment (AWS/Azure/GCP), SSO/SAML authentication, SLA guarantee, and custom connector engineering.", body_style),
            Paragraph("Custom Quote", body_style)
        ]
    ]

    srv_table = Table(services_data, colWidths=[140, 280, 90])
    srv_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(srv_table)
    story.append(Spacer(1, 10))

    # Section 3: How it Works
    story.append(Paragraph("3. How It Works (The 3-Step Journey)", h1_style))
    story.append(Paragraph("<b>Step 1: Connect Your Data:</b> Upload CSV, Excel, or Parquet files, or connect your company SQL database.", bullet_style))
    story.append(Paragraph("<b>Step 2: Ask Anything:</b> Type any business question in plain English. NexaData translates it to sandboxed SQL with self-healing accuracy.", bullet_style))
    story.append(Paragraph("<b>Step 3: Executive Reporting:</b> Instantly receive interactive charts, tabular results, and one-click C-suite PDF/Excel downloads.", bullet_style))

    # Section 4: Policies
    story.append(Paragraph("4. Security, Privacy & Guarantee", h1_style))
    story.append(Paragraph("• <b>Zero Data Leakage:</b> Customer dataset rows are never used for AI model training. Queries execute in sandboxed environments.", bullet_style))
    story.append(Paragraph("• <b>Satisfaction Guarantee:</b> All subscription plans carry a 14-day 100% money-back satisfaction guarantee.", bullet_style))
    story.append(Paragraph("• <b>Support Contact:</b> Support is reachable 24/7 at support@nexadata.ai or via the NexaData AI Assistant.", bullet_style))

    doc.build(story)
    print(f"Sample PDF successfully generated at: {pdf_path}")

if __name__ == "__main__":
    create_nexadata_pdf()
