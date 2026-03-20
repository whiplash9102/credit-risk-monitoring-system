"""
ThanhPham_CreditRisk_Report.pdf
Internal Risk Committee Report — Credit Risk Monitoring
Global Clearing House | Credit & Counterparty Risk Division
Reference Date: 31 December 2025
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os

# ─── COLOUR PALETTE ────────────────────────────────────────────────────────────
NAVY        = HexColor("#0B1F3A")   # primary dark
NAVY_LIGHT  = HexColor("#1A3560")   # header accent
STEEL       = HexColor("#2C4A7C")   # section bar
SILVER      = HexColor("#F4F6FA")   # table alt row
MID_GREY    = HexColor("#8A97A8")   # subtext
LINE_GREY   = HexColor("#D0D8E4")   # dividers
WHITE       = colors.white

RED_ALERT   = HexColor("#C0392B")   # Escalate / CCC
AMBER_ALERT = HexColor("#E67E22")   # Review / B
GREEN_OK    = HexColor("#1E8449")   # Monitor / IG
BLUE_NOTE   = HexColor("#1A6FA5")   # BBB
GOLD        = HexColor("#B8860B")   # BB

RATING_COLOR = {
    "AA": HexColor("#1E5799"), "A": BLUE_NOTE, "BBB": HexColor("#2980B9"),
    "BB": GOLD, "B": AMBER_ALERT, "CCC": RED_ALERT
}

ACTION_COLOR = {
    "Monitor":  GREEN_OK,
    "Review":   AMBER_ALERT,
    "Escalate": RED_ALERT,
}

# ─── PAGE TEMPLATE ─────────────────────────────────────────────────────────────
OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ThanhPham_CreditRisk_Report.pdf"
)

W, H = A4
MARGIN_L = 2.0 * cm
MARGIN_R = 2.0 * cm
MARGIN_T = 1.2 * cm
MARGIN_B = 1.6 * cm
CONTENT_W = W - MARGIN_L - MARGIN_R


def draw_page_frame(canvas_obj, doc):
    """Header bar + footer on every page."""
    canvas_obj.saveState()
    # thin top rule
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, H - 0.55 * cm, W, 0.55 * cm, fill=1, stroke=0)
    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont("Helvetica-Bold", 7)
    canvas_obj.drawString(MARGIN_L, H - 0.38 * cm,
                          "INTERNAL — CREDIT RISK COMMITTEE USE ONLY")
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawRightString(W - MARGIN_R, H - 0.38 * cm,
                               "GCH Credit & Counterparty Risk Division")

    # footer rule
    canvas_obj.setStrokeColor(LINE_GREY)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(MARGIN_L, MARGIN_B - 0.2 * cm,
                    W - MARGIN_R, MARGIN_B - 0.2 * cm)
    canvas_obj.setFillColor(MID_GREY)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawString(MARGIN_L, MARGIN_B - 0.45 * cm,
                          "Credit Risk Monitoring Report | Ref. Date: 31 December 2025")
    canvas_obj.drawRightString(W - MARGIN_R, MARGIN_B - 0.45 * cm,
                               f"Page {doc.page}")
    canvas_obj.restoreState()


# ─── STYLE DEFINITIONS ─────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "cover_title": S("cover_title",
            fontName="Helvetica-Bold", fontSize=22,
            textColor=WHITE, leading=28, alignment=TA_LEFT),
        "cover_sub": S("cover_sub",
            fontName="Helvetica", fontSize=11,
            textColor=HexColor("#A8C0DC"), leading=16, alignment=TA_LEFT),
        "cover_meta": S("cover_meta",
            fontName="Helvetica", fontSize=9,
            textColor=HexColor("#C8D8EC"), leading=13, alignment=TA_LEFT),

        "section_header": S("section_header",
            fontName="Helvetica-Bold", fontSize=11,
            textColor=WHITE, leading=14, alignment=TA_LEFT,
            spaceBefore=0, spaceAfter=0),
        "subsection": S("subsection",
            fontName="Helvetica-Bold", fontSize=9.5,
            textColor=NAVY, leading=13, spaceBefore=8, spaceAfter=3),
        "body": S("body",
            fontName="Helvetica", fontSize=8,
            textColor=HexColor("#1A1A2E"), leading=12,
            alignment=TA_JUSTIFY, spaceAfter=3),
        "bullet": S("bullet",
            fontName="Helvetica", fontSize=8,
            textColor=HexColor("#1A1A2E"), leading=12,
            leftIndent=12, firstLineIndent=0,
            bulletIndent=0, spaceAfter=2),
        "table_header": S("table_header",
            fontName="Helvetica-Bold", fontSize=8,
            textColor=WHITE, leading=11, alignment=TA_CENTER),
        "table_cell": S("table_cell",
            fontName="Helvetica", fontSize=8,
            textColor=HexColor("#1A1A2E"), leading=11, alignment=TA_LEFT),
        "table_cell_c": S("table_cell_c",
            fontName="Helvetica", fontSize=8,
            textColor=HexColor("#1A1A2E"), leading=11, alignment=TA_CENTER),
        "table_cell_bold": S("table_cell_bold",
            fontName="Helvetica-Bold", fontSize=8,
            textColor=NAVY, leading=11, alignment=TA_LEFT),
        "caption": S("caption",
            fontName="Helvetica-Oblique", fontSize=7.5,
            textColor=MID_GREY, leading=10, alignment=TA_CENTER,
            spaceAfter=6),
        "disclaimer": S("disclaimer",
            fontName="Helvetica-Oblique", fontSize=7,
            textColor=MID_GREY, leading=10, alignment=TA_LEFT),
    }


# ─── HELPER FLOWABLES ──────────────────────────────────────────────────────────
class SectionHeader(Flowable):
    """Full-width navy bar with white title."""
    def __init__(self, number, title, width):
        super().__init__()
        self.number = number
        self.title = title
        self.width = width
        self.height = 0.65 * cm

    def draw(self):
        self.canv.setFillColor(STEEL)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        self.canv.setFillColor(WHITE)
        self.canv.setFont("Helvetica-Bold", 10)
        self.canv.drawString(0.3 * cm, 0.18 * cm,
                             f"  {self.number}  {self.title.upper()}")

    def wrap(self, *args):
        return self.width, self.height + 4


def rating_badge(rating, styles):
    """Coloured rating badge as a mini-table."""
    col = RATING_COLOR.get(rating, MID_GREY)
    t = Table([[Paragraph(f"<b>{rating}</b>",
                          ParagraphStyle("rb", fontName="Helvetica-Bold",
                                         fontSize=8, textColor=WHITE,
                                         alignment=TA_CENTER))]],
              colWidths=[1.1 * cm], rowHeights=[0.42 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), col),
        ("ROUNDEDCORNERS", [3]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def action_badge(action):
    col = ACTION_COLOR.get(action, MID_GREY)
    t = Table([[Paragraph(f"<b>{action.upper()}</b>",
                          ParagraphStyle("ab", fontName="Helvetica-Bold",
                                         fontSize=7.5, textColor=WHITE,
                                         alignment=TA_CENTER))]],
              colWidths=[1.5 * cm], rowHeights=[0.40 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), col),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def hr(width=CONTENT_W, thickness=0.5, color=LINE_GREY):
    return HRFlowable(width=width, thickness=thickness, color=color,
                      spaceAfter=4, spaceBefore=4)


def sp(h=4):
    return Spacer(1, h)


def bullet_para(text, styles):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", styles["bullet"])


# ─── COVER PAGE ────────────────────────────────────────────────────────────────
def draw_cover_page(canvas_obj, doc):
    """Draws the full cover page via canvas callback (page 1)."""
    c = canvas_obj
    c.saveState()
    # Full-page navy background
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Accent bar left edge
    c.setFillColor(HexColor("#1F6AA5"))
    c.rect(0, 0, 0.6 * cm, H, fill=1, stroke=0)

    # Top thin highlight stripe
    c.setFillColor(HexColor("#1F6AA5"))
    c.rect(0.6 * cm, H - 0.4 * cm, W - 0.6 * cm, 0.4 * cm, fill=1, stroke=0)
    c.setFillColor(HexColor("#A8C0DC"))
    c.setFont("Helvetica", 7.5)
    c.drawString(2.2 * cm, H - 0.28 * cm,
                 "INTERNAL — CREDIT RISK COMMITTEE USE ONLY")

    # Institution line — upper area
    c.setFillColor(HexColor("#A8C0DC"))
    c.setFont("Helvetica", 9)
    c.drawString(2.2 * cm, H - 3.2 * cm,
                 "GLOBAL CLEARING HOUSE  |  CREDIT & COUNTERPARTY RISK DIVISION")

    # Report title — moved down for vertical balance
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(2.2 * cm, H - 6.0 * cm, "Credit Risk Monitoring")
    c.setFont("Helvetica-Bold", 22)
    c.drawString(2.2 * cm, H - 7.6 * cm, "Committee Report")

    # Subtitle rule
    c.setFillColor(HexColor("#D4A017"))
    c.rect(2.2 * cm, H - 8.2 * cm, 9 * cm, 0.08 * cm, fill=1, stroke=0)

    # Gold accent line across full width — visual divider
    c.setFillColor(HexColor("#D4A017"))
    c.rect(0.6 * cm, H * 0.48, W - 0.6 * cm, 0.06 * cm, fill=1, stroke=0)

    # Meta block — positioned in lower half of page
    meta = [
        ("Reference Date",        "31 December 2025"),
        ("Report Classification", "Internal — Restricted"),
        ("Portfolio Scope",       "25 Entities  (15 Banks / 10 Sovereigns)"),
        ("Prepared by",           "Thanh Pham  |  Credit Risk Analyst"),
        ("Distribution",          "CRO, Risk Committee, Clearing Members Desk"),
    ]
    y = H * 0.44
    for label, value in meta:
        # label box
        c.setFillColor(HexColor("#122D52"))
        c.rect(2.2 * cm, y - 0.05 * cm, 4.5 * cm, 0.55 * cm, fill=1, stroke=0)
        c.setFillColor(HexColor("#8AAFC8"))
        c.setFont("Helvetica", 7.5)
        c.drawString(2.4 * cm, y + 0.08 * cm, label.upper())
        # value
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(7.2 * cm, y + 0.08 * cm, value)
        y -= 0.72 * cm

    # Bottom disclaimer
    c.setFillColor(HexColor("#4A6B8A"))
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawString(2.2 * cm, 2.2 * cm,
                 "This document is prepared for internal risk committee use only and must not be distributed externally.")
    c.drawString(2.2 * cm, 1.55 * cm,
                 "Ratings and assessments reflect internal model outputs as of the reference date and are subject to revision.")
    c.restoreState()


# ─── DATA ──────────────────────────────────────────────────────────────────────
PORTFOLIO = [
    # name, type, score, rating, alerts, watchlist, cds, action, highlight
    ("JPMorgan Chase",   "Bank",      71.0, "BBB", 1, "No",  "44.1",  "Monitor",  False),
    ("HSBC",             "Bank",      59.0, "BB",  2, "Yes", "58.3",  "Review",   False),
    ("BNP Paribas",      "Bank",      54.3, "B",   1, "Yes", "74.2",  "Review",   False),
    ("Deutsche Bank",    "Bank",      51.3, "B",   1, "Yes", "123.2", "Review",   True),
    ("UniCredit",        "Bank",      63.2, "BB",  0, "No",  "61.3",  "Monitor",  False),
    ("Santander",        "Bank",      59.6, "BB",  1, "Yes", "86.7",  "Review",   False),
    ("ING Group",        "Bank",      65.3, "BBB", 0, "No",  "41.2",  "Monitor",  False),
    ("Societe Generale", "Bank",      48.0, "B",   1, "Yes", "129.2", "Review",   True),
    ("Barclays",         "Bank",      58.5, "BB",  1, "Yes", "78.2",  "Review",   False),
    ("UBS",              "Bank",      64.3, "BB",  0, "No",  "38.5",  "Monitor",  False),
    ("Nordea",           "Bank",      76.2, "A",   0, "No",  "21.3",  "Monitor",  False),
    ("Intesa Sanpaolo",  "Bank",      68.1, "BBB", 0, "No",  "55.7",  "Monitor",  False),
    ("ABN AMRO",         "Bank",      60.0, "BB",  1, "Yes", "70.6",  "Review",   False),
    ("Commerzbank",      "Bank",      55.8, "BB",  2, "Yes", "111.6", "Review",   True),
    ("Monte dei Paschi", "Bank",      36.8, "CCC", 4, "Yes", "306.1", "Escalate", True),
    ("Germany",          "Sovereign", 61.3, "BB",  0, "No",  "12.1",  "Monitor",  False),
    ("France",           "Sovereign", 45.4, "B",   1, "Yes", "39.9",  "Review",   False),
    ("United States",    "Sovereign", 40.1, "B",   1, "Yes", "29.7",  "Review",   False),
    ("United Kingdom",   "Sovereign", 46.1, "B",   1, "Yes", "37.4",  "Review",   False),
    ("Japan",            "Sovereign", 54.1, "B",   1, "Yes", "19.4",  "Review",   False),
    ("Italy",            "Sovereign", 40.6, "B",   2, "Yes", "147.7", "Review",   True),
    ("Spain",            "Sovereign", 50.2, "B",   1, "Yes", "88.6",  "Review",   False),
    ("Greece",           "Sovereign", 42.4, "B",   2, "Yes", "271.5", "Review",   True),
    ("Turkey",           "Sovereign", 46.9, "B",   3, "Yes", "472.9", "Review",   True),
    ("Brazil",           "Sovereign", 56.5, "BB",  2, "Yes", "281.3", "Review",   True),
]

WATCHLIST = [
    {
        "name": "Monte dei Paschi",
        "type": "Bank",
        "score": 36.8,
        "rating": "CCC",
        "reason": "NPL ratio 12.4%, negative ROE (–2.5%), C/I at 88%. Internal score breached CCC threshold. CDS at 306 bp and equity vol above 46% confirm sustained market distress.",
        "cds": "306.1 bp",
        "spread": "342.1 bp",
        "equity_5d": "+0.6%",
        "vol": "46.1%",
        "action": "Escalate",
    },
    {
        "name": "Turkey",
        "type": "Sovereign",
        "score": 46.9,
        "rating": "B",
        "reason": "Inflation at 48%, political risk 7/10, limited FX buffer. CDS at 472.9 bp is the widest in the portfolio; equity vol at 53.5% reflects persistent investor risk aversion.",
        "cds": "472.9 bp",
        "spread": "402.1 bp",
        "equity_5d": "–1.8%",
        "vol": "53.5%",
        "action": "Review",
    },
    {
        "name": "Greece",
        "type": "Sovereign",
        "score": 42.4,
        "rating": "B",
        "reason": "Debt/GDP at 185%, bond spread widening alert active (271.5 bp). Score in lower B range with no near-term upside drivers; fiscal headroom remains constrained.",
        "cds": "271.5 bp",
        "spread": "283.4 bp",
        "equity_5d": "–2.1%",
        "vol": "34.8%",
        "action": "Review",
    },
    {
        "name": "Italy",
        "type": "Sovereign",
        "score": 40.6,
        "rating": "B",
        "reason": "Debt/GDP 144%, structural fiscal deficit, equity –5.3% (5d). CDS at 148 bp reflects sovereign fragility; score trajectory flat with European political tail risk.",
        "cds": "147.7 bp",
        "spread": "158.2 bp",
        "equity_5d": "–5.3%",
        "vol": "31.2%",
        "action": "Review",
    },
    {
        "name": "Societe Generale",
        "type": "Bank",
        "score": 48.0,
        "rating": "B",
        "reason": "Internal B vs external A– (three-notch gap) driven by liquidity ratio drag and high cost structure. CDS at 129 bp aligns with internal view. Weakest French bank in the portfolio.",
        "cds": "129.2 bp",
        "spread": "122.5 bp",
        "equity_5d": "+0.3%",
        "vol": "26.3%",
        "action": "Review",
    },
]


# ─── BUILD REPORT ──────────────────────────────────────────────────────────────
def build_report():
    styles = build_styles()
    story = []

    # ── COVER ── (drawn by onFirstPage callback; PageBreak forces content to page 2)
    story.append(PageBreak())

    # ── 1. EXECUTIVE SUMMARY ───────────────────────────────────────────────────
    story.append(SectionHeader("01", "Executive Summary", CONTENT_W))
    story.append(sp(4))

    summary_bullets = [
        ("<b>Portfolio scope:</b> 25 counterparties monitored (15 banks, 10 sovereigns). "
         "18 entities are currently on the watchlist (72% of portfolio), reflecting elevated "
         "macro uncertainty and persistent spread widening across European credit."),
        ("<b>Tail risk concentration:</b> One entity — Monte dei Paschi (Bank, Italy) — has "
         "been escalated for immediate committee action. CDS at 306 bp, negative ROE, and a "
         "CCC internal rating signal material credit deterioration requiring position review."),
        ("<b>Sub-investment-grade dominance:</b> Only 4 of 25 entities score at BBB or above "
         "under the internal model (Nordea, JPMorgan Chase, ING Group, Intesa Sanpaolo). "
         "The remaining 21 carry sub-IG internal ratings — 11 rated B, "
         "9 rated BB, and 1 CCC."),
        ("<b>Sovereign stress is systemic, not idiosyncratic:</b> Eight of ten sovereigns "
         "are watchlisted. Key constraints include high debt/GDP ratios (Italy 144%, Greece 185%), "
         "weak fiscal balances, and limited FX reserve buffers. Germany remains the sole "
         "sovereign off-watchlist."),
        ("<b>Market signals confirm credit stress:</b> CDS–bond spread correlation stands at "
         "0.98 (30-day). Watchlist entities trade at an average CDS of 135 bp vs. 68 bp for "
         "non-watchlist — a 2x pricing differential validating internal risk segmentation. "
         "Turkey (473 bp) and Brazil (281 bp) represent the widest EM sovereign exposures."),
        ("<b>Overall credit outlook: Stable with selective downside risk.</b> No systemic "
         "stress event is imminent. Risk remains concentrated in specific names rather than "
         "portfolio-wide. Primary watch-points: Italian sovereign trajectory, French bank "
         "profitability, and Monte dei Paschi balance sheet repair."),
    ]

    for b in summary_bullets:
        story.append(bullet_para(b, styles))
        story.append(sp(1))

    story.append(sp(3))

    # Outlook box
    outlook_data = [
        [
            Paragraph("<b>OVERALL PORTFOLIO OUTLOOK</b>", ParagraphStyle("ol",
                fontName="Helvetica-Bold", fontSize=9, textColor=NAVY,
                alignment=TA_CENTER)),
            Paragraph("<b>STABLE</b> — Selective downside risk", ParagraphStyle("os",
                fontName="Helvetica-Bold", fontSize=10,
                textColor=GREEN_OK, alignment=TA_CENTER)),
        ]
    ]
    outlook_table = Table(outlook_data, colWidths=[7 * cm, 9 * cm])
    outlook_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), SILVER),
        ("BACKGROUND", (1, 0), (1, 0), HexColor("#EAF6EE")),
        ("BOX", (0, 0), (-1, -1), 1.0, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(outlook_table)
    story.append(sp(5))

    # ── 2. PORTFOLIO OVERVIEW ──────────────────────────────────────────────────
    story.append(SectionHeader("02", "Portfolio Overview", CONTENT_W))
    story.append(sp(4))

    # Portfolio table
    col_w = [4.4*cm, 2.1*cm, 1.6*cm, 1.7*cm, 1.8*cm, 1.8*cm, 2.6*cm]
    headers = ["Entity", "Type", "Score", "Int. Rating", "CDS (bp)", "Alerts", "Watchlist"]
    header_row = [Paragraph(h, styles["table_header"]) for h in headers]
    rows = [header_row]

    # Sort by score ascending (riskiest first)
    sorted_portfolio = sorted(PORTFOLIO, key=lambda x: x[2])

    for i, (name, etype, score, rating, alerts, wl, cds, action, highlight) in enumerate(sorted_portfolio):
        bg = HexColor("#FEF5F5") if highlight else (SILVER if i % 2 == 0 else WHITE)
        rating_col = RATING_COLOR.get(rating, MID_GREY)
        wl_col = RED_ALERT if wl == "Yes" else GREEN_OK
        alert_col = RED_ALERT if alerts >= 3 else (AMBER_ALERT if alerts >= 2 else NAVY)
        row = [
            Paragraph(f"<b>{name}</b>" if highlight else name, styles["table_cell_bold"] if highlight else styles["table_cell"]),
            Paragraph(etype, styles["table_cell_c"]),
            Paragraph(f"<b>{score:.1f}</b>", ParagraphStyle("sc",
                fontName="Helvetica-Bold" if score < 45 else "Helvetica",
                fontSize=8, textColor=RED_ALERT if score < 40 else AMBER_ALERT if score < 55 else NAVY,
                alignment=TA_CENTER)),
            Paragraph(f"<b>{rating}</b>", ParagraphStyle("rc",
                fontName="Helvetica-Bold", fontSize=8,
                textColor=rating_col, alignment=TA_CENTER)),
            Paragraph(cds, ParagraphStyle("cdsc",
                fontName="Helvetica", fontSize=8,
                textColor=RED_ALERT if float(cds) > 200 else AMBER_ALERT if float(cds) > 100 else NAVY,
                alignment=TA_CENTER)),
            Paragraph(str(alerts), ParagraphStyle("ac",
                fontName="Helvetica-Bold" if alerts > 0 else "Helvetica",
                fontSize=8, textColor=alert_col, alignment=TA_CENTER)),
            Paragraph(wl, ParagraphStyle("wc",
                fontName="Helvetica-Bold", fontSize=8,
                textColor=wl_col, alignment=TA_CENTER)),
        ]
        rows.append(row)

    port_table = Table(rows, colWidths=col_w, repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), STEEL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SILVER]),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    # Highlight MdP row
    for i, row_data in enumerate(sorted_portfolio, 1):
        if row_data[7] == "Escalate":
            ts.append(("BACKGROUND", (0, i), (-1, i), HexColor("#FDECEA")))
            ts.append(("LINEBELOW", (0, i), (-1, i), 1.0, RED_ALERT))
            ts.append(("LINEABOVE", (0, i), (-1, i), 1.0, RED_ALERT))

    port_table.setStyle(TableStyle(ts))
    story.append(port_table)
    story.append(sp(3))
    story.append(Paragraph(
        "Sorted by internal score (ascending). Highlighted rows: Top-5 risk concentration names. "
        "CDS spreads as of 31 December 2025.",
        styles["caption"]))

    story.append(PageBreak())

    # ── 3. WATCHLIST ──────────────────────────────────────────────────────────
    story.append(SectionHeader("03", "Watchlist — Key Monitored Names", CONTENT_W))
    story.append(sp(5))

    story.append(Paragraph(
        "18 entities meet at least one watchlist criterion: (i) internal score below 60, "
        "(ii) non-investment-grade external rating, (iii) two or more active market alerts, "
        "or (iv) score deterioration exceeding 10 points. The five highest-severity names are "
        "detailed below. Remaining 13 names are on active monitor status.",
        styles["body"]))
    story.append(sp(5))

    # Escalate section
    story.append(Paragraph("ESCALATE — Immediate Committee Action Required", ParagraphStyle(
        "esc_hdr", fontName="Helvetica-Bold", fontSize=9,
        textColor=WHITE, backColor=RED_ALERT,
        leftIndent=5, rightIndent=5, leading=14,
        spaceBefore=4, spaceAfter=6)))

    wl_escalate = [e for e in WATCHLIST if e["action"] == "Escalate"]
    for e in wl_escalate:
        _render_watchlist_card(story, e, styles)

    story.append(sp(4))
    story.append(Paragraph("REVIEW — Timely Analytical Action Required", ParagraphStyle(
        "rev_hdr", fontName="Helvetica-Bold", fontSize=9,
        textColor=WHITE, backColor=AMBER_ALERT,
        leftIndent=5, rightIndent=5, leading=14,
        spaceBefore=4, spaceAfter=4)))

    wl_review = [e for e in WATCHLIST if e["action"] == "Review"]
    for e in wl_review:
        _render_watchlist_card(story, e, styles)

    story.append(PageBreak())

    # ── 4. DETAILED CREDIT NOTES ──────────────────────────────────────────────
    story.append(SectionHeader("04", "Detailed Credit Notes", CONTENT_W))
    story.append(sp(5))

    story.append(Paragraph(
        "In-depth assessments for one bank and one sovereign, selected on analytical significance "
        "and committee relevance as of the reference date.",
        styles["body"]))
    story.append(sp(6))

    # 4a. Bank: Monte dei Paschi
    _render_credit_note(story, styles, {
        "name": "Monte dei Paschi di Siena",
        "tag": "Bank | Italy | CCC",
        "tag_color": RED_ALERT,
        "overview": (
            "Italy's third-largest bank by assets. Despite a 2022 state recapitalisation, structural "
            "weaknesses persist: negative profitability, legacy NPLs, and cost rigidity. Sole "
            "'Escalate' entity in the current monitoring cycle."
        ),
        "strengths": [
            "CET1 ratio 18.3% — well above regulatory minima, providing a capital buffer.",
            "Loan-to-deposit ratio 0.95x — balanced funding, limited near-term liquidity cliff.",
            "State backstop preserves systemic relevance; reduces immediate insolvency risk.",
        ],
        "weaknesses": [
            "NPL ratio 12.4% — highest in the bank universe, approximately 4x the portfolio median.",
            "Negative ROE (–2.5%) and C/I at 88.4% indicate structural unprofitability.",
            "CDS at 306 bp and equity vol 46.1% signal persistent market scepticism.",
        ],
        "signals": [
            ("CDS 5Y", "306.1 bp", RED_ALERT),
            ("Bond Spread", "342.1 bp", RED_ALERT),
            ("Equity 5d Return", "+0.6%", GREEN_OK),
            ("Implied Vol (30d)", "46.1%", RED_ALERT),
        ],
        "int_rating": "CCC",
        "ext_rating": "B",
        "outlook": "Negative",
        "analyst_view": (
            "MPS is the portfolio's highest-severity name. The CCC rating reflects genuine "
            "fundamental impairment. Recommend review of exposure limits and collateral terms. "
            "Escalation to default-watch triggered by: NPL >15%, CDS >400 bp sustained, or "
            "regulatory capital call."
        ),
    })

    story.append(sp(10))

    # 4b. Sovereign: Turkey
    _render_credit_note(story, styles, {
        "name": "Republic of Turkey",
        "tag": "Sovereign | EM | B",
        "tag_color": AMBER_ALERT,
        "overview": (
            "Widest CDS in the portfolio at 472.9 bp. Structurally high inflation, political risk, "
            "and limited monetary policy credibility are primary drivers. Internal model assigns B, "
            "broadly in line with external B+ rating."
        ),
        "strengths": [
            "GDP growth 4.2% — above EM peer average, providing a cyclical buffer.",
            "FX reserves stabilised post-2023 policy normalisation; acute external liquidity risk reduced.",
            "Rate hike cycle signals partial restoration of central bank credibility.",
        ],
        "weaknesses": [
            "Inflation at 48% — highest in the sovereign portfolio; primary internal score drag.",
            "Political risk score 7/10; institutional independence of key bodies remains constrained.",
            "CDS at 472.9 bp and equity vol 53.5% — highest in the entire portfolio.",
        ],
        "signals": [
            ("CDS 5Y", "472.9 bp", RED_ALERT),
            ("Bond Spread", "402.1 bp", RED_ALERT),
            ("Equity 5d Return", "–1.8%", AMBER_ALERT),
            ("Implied Vol (30d)", "53.5%", RED_ALERT),
        ],
        "int_rating": "B",
        "ext_rating": "B+",
        "outlook": "Stable / Watchlisted",
        "analyst_view": (
            "Turkey's risk profile is driven by macro variables not resolvable near-term. "
            "Key trigger for reassessment: inflation declining below 30%. Collateral margins should "
            "reflect current CDS levels. Escalation warranted on renewed lira depreciation or "
            "political risk increase."
        ),
    })

    story.append(PageBreak())

    # ── 5. MARKET MONITORING INSIGHTS ─────────────────────────────────────────
    story.append(SectionHeader("05", "Market Monitoring Insights", CONTENT_W))
    story.append(sp(5))

    # Compact 2-column market signal summary table
    mkt_data_rows = [
        [Paragraph("<b>Theme</b>", styles["table_header"]),
         Paragraph("<b>Key Observations</b>", styles["table_header"])],
        [Paragraph("<b>CDS Trends</b>", styles["table_cell_bold"]),
         Paragraph(
             "Elevated but range-bound across Q4 2025; no systemic widening event. Turkey (473 bp) "
             "and MPS (306 bp) persistent throughout. ~48 CDS alerts over 90 days, concentrated "
             "in Oct 8-13 and Dec 18-19 — two discrete stress episodes. Franco-German bank "
             "bifurcation: DB/SocGen 123-129 bp vs. Nordea 21 bp.",
             styles["table_cell"])],
        [Paragraph("<b>Bond Spreads</b>", styles["table_cell_bold"]),
         Paragraph(
             "CDS-bond spread correlation: 0.98 (30-day) — stress expressed entirely through "
             "credit markets. One active alert: Greece (>25 bp 5d widening). Peripheral spreads "
             "(Italy 158 bp, Greece 283 bp, Spain 89 bp) consistent with B-range quality. "
             "US Treasury at 16 bp despite internal B — reserve currency premium not in model.",
             styles["table_cell"])],
        [Paragraph("<b>Equity Vol</b>", styles["table_cell_bold"]),
         Paragraph(
             "Eq-vol/CDS correlation: 0.82. Four entities in elevated vol regime (>35%): "
             "Turkey 53.5%, MPS 46.1%, Brazil 38.7%, Commerzbank 37.2% — all watchlisted. "
             "DM bank vol normalised at 17-26%; no sector-wide stress. Worst 5d returns: "
             "Barclays –5.6%, Italy –5.3%, Brazil –3.2%.",
             styles["table_cell"])],
        [Paragraph("<b>Stress Assessment</b>", styles["table_cell_bold"]),
         Paragraph(
             "Systemic risk: <b>LOW.</b> Idiosyncratic risk: <b>ELEVATED</b> for 7 names. "
             "Watchlist avg CDS 135 bp vs non-watchlist 68 bp (2x differential) — validates model "
             "discriminatory power. No contagion pathway identified. Monitoring framework providing "
             "effective early warning.",
             styles["table_cell"])],
    ]
    mkt_table = Table(mkt_data_rows, colWidths=[3.5*cm, 12.5*cm], repeatRows=1)
    mkt_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), STEEL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SILVER]),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(mkt_table)
    story.append(sp(3))

    story.append(hr())
    story.append(sp(5))

    # ── 6. METHODOLOGY ────────────────────────────────────────────────────────
    story.append(SectionHeader("06", "Methodology", CONTENT_W))
    story.append(sp(5))

    meth_bullets = [
        ("<b>Internal scoring (Banks):</b> A 7-factor weighted composite model (0–100 scale) "
         "combining CET1 ratio (25%), NPL ratio (20%), ROE (15%), leverage (10%), "
         "loan-to-deposit (10%), cost-to-income (10%), and liquidity ratio (10%). Each component "
         "is normalised relative to peer distribution before weighting."),
        ("<b>Internal scoring (Sovereigns):</b> Seven macro-fiscal factors — debt/GDP (25%), "
         "fiscal balance (20%), inflation (15%), FX reserves (15%), GDP growth (10%), political "
         "risk (10%), and current account (5%) — calibrated to reflect structural credit capacity "
         "rather than market price signals alone."),
        ("<b>Rating mapping:</b> Score ranges map to AA (85–100), A (75–84), BBB (65–74), "
         "BB (55–64), B (40–54), and CCC (<40). The thresholds are calibrated to align with "
         "historical agency rating distributions across comparable peer sets."),
        ("<b>Market alerts:</b> Four independent triggers — CDS widening >20 bp over 5 days; "
         "bond spread widening >25 bp over 5 days; 5-day equity return below –10%; and 30-day "
         "implied equity volatility above 35%. Alerts are additive: four active alerts indicates "
         "maximum market stress."),
        ("<b>Watchlist logic:</b> An entity is watchlisted if it meets at least one of: internal "
         "score below 60, non-investment-grade external rating, two or more concurrent market "
         "alerts, or a score deterioration exceeding 10 points versus prior snapshot. Priority "
         "tier (Monitor / Review / Escalate) is determined by combined signal severity."),
        ("<b>Limitations:</b> The internal model is designed for relative risk ranking within "
         "a clearing house context, not absolute default probability estimation. Model outputs "
         "should be read alongside external agency ratings, qualitative intelligence, and "
         "margin model outputs before any exposure or collateral decision is taken."),
    ]

    for b in meth_bullets:
        story.append(bullet_para(b, styles))
        story.append(sp(3))

    story.append(sp(8))
    story.append(hr(thickness=0.3))
    story.append(sp(5))
    story.append(Paragraph(
        "This report was prepared by Thanh Pham, Credit Risk Analyst. All ratings, scores, and "
        "market signals are based on the internal credit risk monitoring framework as of "
        "31 December 2025. Internal ratings do not constitute investment advice and are prepared "
        "for risk management purposes only. Reproduction or external distribution is prohibited.",
        styles["disclaimer"]))

    return story


# ─── WATCHLIST CARD RENDERER ───────────────────────────────────────────────────
def _render_watchlist_card(story, e, styles):
    action_col = ACTION_COLOR.get(e["action"], MID_GREY)
    rating_col = RATING_COLOR.get(e["rating"], MID_GREY)

    # Header row
    name_style = ParagraphStyle("wn", fontName="Helvetica-Bold", fontSize=9,
                                 textColor=NAVY, leading=13)
    tag_style = ParagraphStyle("wt", fontName="Helvetica", fontSize=8,
                                textColor=MID_GREY, leading=11)
    header_data = [[
        Paragraph(e["name"], name_style),
        Paragraph(f"Score: <b>{e['score']:.1f}</b>  |  {e['type']}", tag_style),
        Paragraph(f"<b>{e['rating']}</b>", ParagraphStyle("wr",
            fontName="Helvetica-Bold", fontSize=9, textColor=rating_col,
            alignment=TA_CENTER)),
        Paragraph(f"<b>{e['action'].upper()}</b>", ParagraphStyle("wa",
            fontName="Helvetica-Bold", fontSize=8.5, textColor=action_col,
            alignment=TA_CENTER)),
    ]]
    hdr_table = Table(header_data, colWidths=[5.5*cm, 6.0*cm, 2.0*cm, 2.5*cm])
    hdr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SILVER),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(hdr_table)

    # Reason + signals row
    reason_para = Paragraph(e["reason"], ParagraphStyle("wr2",
        fontName="Helvetica", fontSize=8, textColor=HexColor("#1A1A2E"),
        leading=12, leftIndent=4))

    signals_data = [
        [Paragraph("<b>CDS</b>", styles["table_cell_bold"]),
         Paragraph(e["cds"], styles["table_cell_c"])],
        [Paragraph("<b>Spread</b>", styles["table_cell_bold"]),
         Paragraph(e["spread"], styles["table_cell_c"])],
        [Paragraph("<b>Eq 5d</b>", styles["table_cell_bold"]),
         Paragraph(e["equity_5d"], styles["table_cell_c"])],
        [Paragraph("<b>Vol</b>", styles["table_cell_bold"]),
         Paragraph(e["vol"], styles["table_cell_c"])],
    ]
    sig_table = Table(signals_data, colWidths=[1.8*cm, 1.8*cm])
    sig_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.3, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, SILVER]),
    ]))

    body_data = [[reason_para, sig_table]]
    body_table = Table(body_data, colWidths=[12.2*cm, 3.8*cm])
    body_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("LINEABOVE", (0, 0), (-1, 0), 0, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(body_table)
    story.append(sp(6))


# ─── CREDIT NOTE RENDERER ──────────────────────────────────────────────────────
def _render_credit_note(story, styles, note):
    # Title bar
    title_data = [[
        Paragraph(note["name"], ParagraphStyle("cn_name",
            fontName="Helvetica-Bold", fontSize=11,
            textColor=NAVY, leading=14)),
        Paragraph(note["tag"], ParagraphStyle("cn_tag",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=WHITE, backColor=note["tag_color"],
            leading=14, alignment=TA_RIGHT)),
    ]]
    title_table = Table(title_data, colWidths=[CONTENT_W * 0.62, CONTENT_W * 0.38])
    title_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), SILVER),
        ("BACKGROUND", (1, 0), (1, 0), note["tag_color"]),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(title_table)
    story.append(sp(6))

    # Overview
    story.append(Paragraph(note["overview"], styles["body"]))
    story.append(sp(6))

    # Strengths + Weaknesses (two-column) — each half of CONTENT_W
    HALF_W = CONTENT_W / 2

    def strength_weak_block(items, header, hcol, bcol, col_w):
        content = [[Paragraph(header, ParagraphStyle("sh",
            fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE,
            alignment=TA_CENTER))]]
        for item in items:
            content.append([Paragraph(item,
                ParagraphStyle("si", fontName="Helvetica", fontSize=8,
                    textColor=HexColor("#1A1A2E"), leading=12,
                    leftIndent=4, spaceAfter=2))])
        t = Table(content, colWidths=[col_w])
        ts = [
            ("BACKGROUND", (0, 0), (-1, 0), hcol),
            ("BACKGROUND", (0, 1), (-1, -1), bcol),
            ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        t.setStyle(TableStyle(ts))
        return t

    sw_data = [[
        strength_weak_block(note["strengths"], "STRENGTHS", GREEN_OK,
                            HexColor("#EAF6EE"), HALF_W),
        strength_weak_block(note["weaknesses"], "WEAKNESSES", RED_ALERT,
                            HexColor("#FEF5F5"), HALF_W),
    ]]
    sw_table = Table(sw_data, colWidths=[HALF_W, HALF_W])
    sw_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("INNERGRID", (0, 0), (-1, -1), 0, WHITE),
    ]))
    story.append(sw_table)
    story.append(sp(8))

    # Market signals + Rating
    sig_header = [Paragraph("MARKET SIGNALS — 31 DEC 2025", ParagraphStyle("msh",
        fontName="Helvetica-Bold", fontSize=8, textColor=WHITE,
        alignment=TA_CENTER))]
    sig_rows = [sig_header]
    for label, value, vcol in note["signals"]:
        sig_rows.append([
            Table([[
                Paragraph(label, ParagraphStyle("sl",
                    fontName="Helvetica", fontSize=8, textColor=MID_GREY)),
                Paragraph(f"<b>{value}</b>", ParagraphStyle("sv",
                    fontName="Helvetica-Bold", fontSize=8, textColor=vcol,
                    alignment=TA_RIGHT)),
            ]], colWidths=[3.5*cm, 3.0*cm],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("TOPPADDING", (0, 0), (-1, -1), 2),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 2),]))
        ])

    # Column widths for the 3-column bottom block
    # CONTENT_W ≈ 17.0 cm  →  5.5 + 3.5 + 8.0 = 17.0 cm
    SIG_W  = 5.5 * cm
    RTG_W  = 3.5 * cm
    ANL_W  = CONTENT_W - SIG_W - RTG_W   # remaining width for analyst view

    # Inner signal label/value widths (must sum < SIG_W accounting for cell padding)
    sig_inner_label = 3.0 * cm
    sig_inner_value = SIG_W - sig_inner_label - 0.3 * cm  # small breathing room

    # Rebuild sig rows with correct inner widths
    sig_rows2 = [sig_header]
    for label, value, vcol in note["signals"]:
        sig_rows2.append([
            Table([[
                Paragraph(label, ParagraphStyle("sl2",
                    fontName="Helvetica", fontSize=8, textColor=MID_GREY)),
                Paragraph(f"<b>{value}</b>", ParagraphStyle("sv2",
                    fontName="Helvetica-Bold", fontSize=8, textColor=vcol,
                    alignment=TA_RIGHT)),
            ]], colWidths=[sig_inner_label, sig_inner_value],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("TOPPADDING", (0, 0), (-1, -1), 2),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 0),]))
        ])

    sig_table = Table(sig_rows2, colWidths=[SIG_W])
    sig_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), STEEL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SILVER]),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    rating_data = [
        [Paragraph("INT. RATING", ParagraphStyle("ir_hdr",
            fontName="Helvetica-Bold", fontSize=8, textColor=WHITE,
            alignment=TA_CENTER))],
        [Paragraph(note["int_rating"], ParagraphStyle("ir_val",
            fontName="Helvetica-Bold", fontSize=22,
            textColor=RATING_COLOR.get(note["int_rating"], NAVY),
            alignment=TA_CENTER))],
        [Paragraph(f"Ext: {note['ext_rating']}", ParagraphStyle("ir_ext",
            fontName="Helvetica", fontSize=7.5, textColor=MID_GREY,
            alignment=TA_CENTER))],
        [Paragraph(f"<b>{note['outlook']}</b>", ParagraphStyle("ir_out",
            fontName="Helvetica-Bold", fontSize=7.5,
            textColor=RED_ALERT if "Neg" in note["outlook"] else NAVY,
            alignment=TA_CENTER))],
    ]
    r_table = Table(rating_data, colWidths=[RTG_W])
    r_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), STEEL),
        ("BACKGROUND", (0, 1), (-1, -1), SILVER),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # Analyst view: inner width = ANL_W minus outer cell horizontal padding (12pt total)
    anl_inner_w = ANL_W - 12
    analyst_data = [
        [Paragraph("ANALYST VIEW", ParagraphStyle("av_hdr",
            fontName="Helvetica-Bold", fontSize=8, textColor=WHITE,
            alignment=TA_CENTER))],
        [Paragraph(note["analyst_view"], ParagraphStyle("av_body",
            fontName="Helvetica-Oblique", fontSize=8,
            textColor=HexColor("#1A1A2E"), leading=12))],
    ]
    a_table = Table(analyst_data, colWidths=[anl_inner_w])
    a_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#F0F4FA")),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    bottom_data = [[sig_table, r_table, a_table]]
    bottom_table = Table(bottom_data, colWidths=[SIG_W, RTG_W, ANL_W])
    bottom_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bottom_table)


# ─── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=MARGIN_T + 0.55 * cm,   # header bar height included
        bottomMargin=MARGIN_B + 0.35 * cm,
        title="Credit Risk Monitoring Report — Internal",
        author="Thanh Pham | GCH Credit Risk Division",
        subject="Internal Credit Risk Committee Report — 31 December 2025",
    )

    story = build_report()
    doc.build(story, onFirstPage=draw_cover_page, onLaterPages=draw_page_frame)
    print(f"Report generated: {OUTPUT_PATH}")
