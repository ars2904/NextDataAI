"""NexaData AI Conversation PDF Export Module.

Generates branded, beautifully formatted PDF transcripts of user chats using ReportLab.
"""
import io
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

BASE_DIR = Path(__file__).resolve().parent.parent

def clean_markdown_text(text: str) -> str:
    """Convert common Markdown syntax into clean formatted text for ReportLab Paragraphs."""
    if not text:
        return ""

    # Escape HTML special chars first
    cleaned = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Convert bold **text** to <b>text</b>
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cleaned)

    # Convert italic *text* or _text_ to <i>text</i>
    cleaned = re.sub(r'\*(.*?)\*', r'<i>\1</i>', cleaned)
    cleaned = re.sub(r'_(.*?)_', r'<i>\1</i>', cleaned)

    # Convert inline code `code` to <font name="Courier">code</font>
    cleaned = re.sub(r'`(.*?)`', r'<font name="Courier" color="#0284C7"><b>\1</b></font>', cleaned)

    # Convert headers ### to bold titles
    cleaned = re.sub(r'^###\s+(.*)$', r'<br/><b><font size="11" color="#0369A1">\1</font></b><br/>', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^##\s+(.*)$', r'<br/><b><font size="12" color="#0284C7">\1</font></b><br/>', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^#\s+(.*)$', r'<br/><b><font size="13" color="#0284C7">\1</font></b><br/>', cleaned, flags=re.MULTILINE)

    # Convert bullet points
    cleaned = re.sub(r'^\s*[-*]\s+(.*)$', r'&bull; \1<br/>', cleaned, flags=re.MULTILINE)

    # Convert newlines to breaks
    cleaned = cleaned.replace("\n\n", "<br/><br/>").replace("\n", "<br/>")

    return cleaned


class NumberedCanvas:
    """Two-pass canvas to add accurate page count footers."""
    pass


def generate_conversation_pdf(
    title: str,
    mode: str,
    messages: List[Dict[str, Any]],
    export_time: Optional[str] = None
) -> bytes:
    """Generate a high-quality PDF transcript for a conversation thread."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    style_brand = ParagraphStyle(
        'BrandHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0284C7')
    )

    style_tagline = ParagraphStyle(
        'BrandTagline',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B')
    )

    style_meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569')
    )

    style_meta_val = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A')
    )

    style_user_name = ParagraphStyle(
        'UserName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0369A1')
    )

    style_user_msg = ParagraphStyle(
        'UserMsg',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#0F172A')
    )

    style_bot_name = ParagraphStyle(
        'BotName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0284C7')
    )

    style_bot_msg = ParagraphStyle(
        'BotMsg',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    style_source_box = ParagraphStyle(
        'SourceBox',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0369A1')
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("🧠 <b>NexaData AI</b>", style_brand),
            Paragraph(f"<b>Exported:</b> {export_time or datetime.now().strftime('%b %d, %Y - %I:%M %p')}", style_meta_val)
        ],
        [
            Paragraph("<i>Ask. Analyze. Discover. — Enterprise Intelligence</i>", style_tagline),
            Paragraph(f"<b>Mode:</b> {mode.title()} Questions", style_meta_val)
        ]
    ]

    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=10))

    # 2. Metadata Box
    meta_box_data = [
        [
            Paragraph("<b>Conversation Topic:</b>", style_meta_label),
            Paragraph(title or "Active Conversation", style_meta_val),
            Paragraph("<b>Messages Count:</b>", style_meta_label),
            Paragraph(str(len(messages)), style_meta_val),
        ]
    ]
    meta_table = Table(meta_box_data, colWidths=[120, 240, 100, 80])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Conversation Messages
    if not messages:
        story.append(Paragraph("<i>No messages in this conversation yet.</i>", style_meta_val))
    else:
        for idx, msg in enumerate(messages, 1):
            is_user = msg.get("type") == "user" or msg.get("role") == "user"
            msg_text = msg.get("text") or msg.get("reply") or msg.get("content") or ""
            timestamp = msg.get("timestamp") or ""
            sources = msg.get("sources") or []

            clean_text = clean_markdown_text(msg_text)
            att = msg.get("attachment") or msg.get("attachment_info") or {}
            att_name = att.get("name") or att.get("filename")
            if att_name:
                att_size = f" ({att.get('size')})" if att.get("size") else ""
                clean_text = f"<b>[📎 Attached: {att_name}{att_size}]</b><br/><br/>{clean_text}"

            if is_user:
                # User Prompt Card
                card_data = [
                    [Paragraph(f"👤 <b>User Prompt</b> &nbsp;&nbsp;<font size='7' color='#64748B'>{timestamp}</font>", style_user_name)],
                    [Paragraph(clean_text, style_user_msg)]
                ]
                msg_table = Table(card_data, colWidths=[540])
                msg_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F9FF')),
                    ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#BAE6FD')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
            else:
                # Assistant Response Card
                content_rows = [
                    [Paragraph(f"🤖 <b>NexaData AI Response</b> &nbsp;&nbsp;<font size='7' color='#64748B'>{timestamp}</font>", style_bot_name)],
                    [Paragraph(clean_text, style_bot_msg)]
                ]

                # If source citations present
                if sources:
                    s0 = sources[0]
                    src_label = f"📄 <b>Grounded Source:</b> {s0.get('document', 'Official Documents')} (Page {s0.get('page', 1)})"
                    content_rows.append([
                        Paragraph(f"<font color='#0284C7'>{src_label}</font>", style_source_box)
                    ])

                msg_table = Table(content_rows, colWidths=[540])
                msg_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFFFF')),
                    ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#E2E8F0')),
                    ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.HexColor('#F1F5F9')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))

            story.append(KeepTogether(msg_table))
            story.append(Spacer(1, 10))

    # Page numbering & footer hook
    def add_footer(canvas, document):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#94A3B8'))
        # Footer text
        footer_text = f"NexaData AI Assistant — Confidential & Enterprise Proprietary — Page {document.page}"
        canvas.drawCentredString(letter[0] / 2.0, 25, footer_text)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer.getvalue()
