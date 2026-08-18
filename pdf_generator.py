from io import BytesIO
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)


# =========================================================
# FONT SETUP
# =========================================================

FONT_FOLDER = "fonts"

regular_font = os.path.join(
    FONT_FOLDER,
    "DejaVuSans.ttf"
)

bold_font = os.path.join(
    FONT_FOLDER,
    "DejaVuSans-Bold.ttf"
)


if os.path.exists(regular_font) and os.path.exists(bold_font):

    pdfmetrics.registerFont(
        TTFont("DejaVu", regular_font)
    )

    pdfmetrics.registerFont(
        TTFont("DejaVu-Bold", bold_font)
    )

    FONT_REGULAR = "DejaVu"
    FONT_BOLD = "DejaVu-Bold"

else:

    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"


# =========================================================
# CREATE PDF
# =========================================================

def create_pdf(summary, title="YouTube Video Summary"):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,

        rightMargin=25 * mm,
        leftMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,

        title=title,
        author="YouTube Video Summarizer"
    )


    # =====================================================
    # TITLE STYLE
    # =====================================================

    title_style = ParagraphStyle(
        "DocumentTitle",

        fontName=FONT_BOLD,
        fontSize=17,
        leading=22,

        alignment=TA_LEFT,

        textColor=colors.black,

        spaceAfter=18
    )


    # =====================================================
    # SUBHEADING STYLE
    # =====================================================

    subheading_style = ParagraphStyle(
        "SubHeading",

        fontName=FONT_BOLD,

        # Same type of size as the "Conclusion"
        # heading in your reference PDF
        fontSize=13,

        leading=18,

        alignment=TA_LEFT,

        textColor=colors.black,

        spaceBefore=16,
        spaceAfter=12
    )


    # =====================================================
    # BODY STYLE
    # =====================================================

    body_style = ParagraphStyle(
        "Body",

        fontName=FONT_REGULAR,

        fontSize=10.5,

        leading=17,

        alignment=TA_LEFT,

        textColor=colors.black,

        spaceAfter=14
    )


    # =====================================================
    # BULLET STYLE
    # =====================================================

    bullet_style = ParagraphStyle(
        "Bullet",

        fontName=FONT_REGULAR,

        fontSize=10.5,

        leading=17,

        leftIndent=15,
        firstLineIndent=-8,

        textColor=colors.black,

        spaceAfter=9
    )


    story = []


    # =====================================================
    # DOCUMENT TITLE
    # =====================================================

    title = str(title).strip()

    if not title:
        title = "YouTube Video Summary"

    story.append(
        Paragraph(
            escape_text(title),
            title_style
        )
    )


    # =====================================================
    # AI SUMMARY
    # =====================================================

    story.append(
        Paragraph(
            "AI Summary",
            subheading_style
        )
    )


    summary = str(summary).strip()

    summary = summary.replace("\r\n", "\n")
    summary = summary.replace("\r", "\n")


    # =====================================================
    # PROCESS SUMMARY
    # =====================================================

    lines = summary.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            continue


        # -------------------------------------------------
        # SUBHEADING
        # -------------------------------------------------
        #
        # Example:
        #
        # **Conclusion**
        #
        # **Key Findings**
        #
        # **Impact on Society**
        #
        # -------------------------------------------------

        heading_match = re.fullmatch(
            r"\*\*(.+?)\*\*",
            line
        )

        if heading_match:

            heading_text = heading_match.group(1).strip()

            story.append(
                Paragraph(
                    escape_text(heading_text),
                    subheading_style
                )
            )

            continue


        # -------------------------------------------------
        # BULLET POINT
        # -------------------------------------------------

        if re.match(r"^[-•*]\s+", line):

            bullet_text = re.sub(
                r"^[-•*]\s+",
                "",
                line
            )

            bullet_text = convert_bold(
                bullet_text
            )

            story.append(
                Paragraph(
                    "• " + bullet_text,
                    bullet_style
                )
            )

            continue


        # -------------------------------------------------
        # NORMAL PARAGRAPH
        # -------------------------------------------------

        paragraph_text = convert_bold(line)

        story.append(
            Paragraph(
                paragraph_text,
                body_style
            )
        )


    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(story)

    pdf_bytes = buffer.getvalue()

    buffer.close()

    return pdf_bytes


# =========================================================
# ESCAPE TEXT
# =========================================================

def escape_text(text):

    text = str(text)

    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    return text


# =========================================================
# CONVERT **TEXT** TO BOLD
# =========================================================

def convert_bold(text):

    text = escape_text(text)

    # Convert:
    #
    # **important point**
    #
    # into:
    #
    # <b>important point</b>

    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        text
    )

    return text