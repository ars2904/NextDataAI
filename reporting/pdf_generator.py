"""Executive PDF Report Generator for NexaData AI."""
import io
import html
from datetime import datetime
from typing import Optional
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether
)


def generate_executive_pdf(
    question: str,
    query: str,
    df_result: pd.DataFrame,
    dataset_name: str = "datainfo.csv",
    chart_image_bytes: Optional[bytes] = None,
    summary_insight: Optional[str] = None
) -> bytes:
    """
    Generate an executive-ready landscape A4 PDF report with branding,
    question metadata, SQL query, embedded chart, and styled data table.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=35,
        rightMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        "ExecTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        "ExecSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B")
    )
    
    h2_style = ParagraphStyle(
        "ExecH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=10,
        spaceAfter=6
    )
    
    code_box_style = ParagraphStyle(
        "ExecCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0F172A")
    )
    
    table_cell_style = ParagraphStyle(
        "ExecTableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1E293B")
    )
    
    table_header_style = ParagraphStyle(
        "ExecTableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []

    # 1. Header Banner & Metadata
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    header_data = [
        [
            Paragraph("<b>NexaData AI</b> | Executive Data Report", title_style),
            Paragraph(f"<b>Generated:</b> {now_str}<br/><b>Source:</b> {html.escape(dataset_name)}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[520, 220])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#2563EB")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # 2. Analytical Question Asked
    story.append(Paragraph("Analytical Question", h2_style))
    question_clean = html.escape(question)
    q_table = Table([[Paragraph(f"<b>&ldquo;{question_clean}&rdquo;</b>", table_cell_style)]], colWidths=[740])
    q_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(q_table)
    story.append(Spacer(1, 10))

    # 3. Executed Query Box
    story.append(Paragraph("Executed Analytical Query (DuckDB SQL)", h2_style))
    query_clean = html.escape(query).replace("\n", "<br/>")
    code_table = Table([[Paragraph(query_clean, code_box_style)]], colWidths=[740])
    code_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(code_table)
    story.append(Spacer(1, 12))

    # 4. Embedded Chart (if available)
    if chart_image_bytes:
        try:
            chart_io = io.BytesIO(chart_image_bytes)
            chart_img = RLImage(chart_io, width=700, height=300)
            story.append(KeepTogether([
                Paragraph("Data Visualization", h2_style),
                chart_img,
                Spacer(1, 12)
            ]))
        except Exception:
            pass

    # 5. Tabular Results (Preview up to 60 rows for clean PDF pagination)
    if df_result is not None and len(df_result) > 0:
        story.append(Paragraph(f"Analytical Findings ({len(df_result):,} total records)", h2_style))
        
        display_df = df_result.head(60)
        num_cols = len(display_df.columns)
        available_width = 740
        col_w = available_width / max(num_cols, 1)

        # Prepare table rows
        table_rows = []
        
        # Header Row
        header_cells = [
            Paragraph(f"<b>{html.escape(str(c))}</b>", table_header_style)
            for c in display_df.columns
        ]
        table_rows.append(header_cells)
        
        # Data Rows
        for row in display_df.itertuples(index=False, name=None):
            row_cells = [
                Paragraph(html.escape(str(v)), table_cell_style)
                for v in row
            ]
            table_rows.append(row_cells)

        res_table = Table(table_rows, colWidths=[col_w] * num_cols, repeatRows=1)
        res_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#94A3B8")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(res_table)
        
        if len(df_result) > 60:
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<i>* Note: Displaying first 60 rows in PDF. Full dataset available in Excel export.</i>", subtitle_style))

    # Build PDF Document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
