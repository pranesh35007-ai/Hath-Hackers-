import io
import datetime
import html
import re

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)

from backend.data_engine import profile, likely_measure
from backend.statistics_engine import descriptive, zscore_outliers
from backend.ai_agent import executive_insights


# ---------------------------------------------------------------------------
# Business-report helpers
# ---------------------------------------------------------------------------

NAVY = "#0B1730"
INK = "#17243B"
MUTED = "#64748B"
BLUE = "#2563EB"
TEAL = "#0F9F9A"
GREEN = "#16A34A"
AMBER = "#D97706"
RED = "#DC2626"
LINE = "#DCE4EE"
SOFT = "#F5F8FC"
WHITE = "#FFFFFF"


def _safe_text(value):
    return html.escape("" if value is None else str(value))


def _fmt_number(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K"
        if value.is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}"
    except Exception:
        return str(value)


def _clean_ai_markdown(text):
    """Convert the AI markdown into short, readable report paragraphs."""
    if not text:
        return []
    lines = []
    for raw in str(text).splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"^\s*[-*]\s+", "• ", line)
        line = re.sub(r"^\s*\d+\.\s+", "", line)
        if line:
            lines.append(line)
    return lines


def _report_metrics(df):
    p = profile(df)
    measure = likely_measure(df)
    missing_rate = (p["missing"] / max(p["rows"] * p["columns"], 1)) * 100
    return p, measure, missing_rate


def _report_styles():
    styles = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title", parent=styles["Title"], fontName="Helvetica-Bold",
            fontSize=28, leading=32, textColor=colors.HexColor(NAVY),
            alignment=TA_LEFT, spaceAfter=8
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=styles["Normal"], fontName="Helvetica",
            fontSize=11, leading=16, textColor=colors.HexColor(MUTED),
            spaceAfter=5
        ),
        "section": ParagraphStyle(
            "section", parent=styles["Heading2"], fontName="Helvetica-Bold",
            fontSize=15, leading=19, textColor=colors.HexColor(NAVY),
            spaceBefore=12, spaceAfter=7
        ),
        "subsection": ParagraphStyle(
            "subsection", parent=styles["Heading3"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=14, textColor=colors.HexColor(BLUE),
            spaceBefore=7, spaceAfter=5
        ),
        "body": ParagraphStyle(
            "body", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=9.2, leading=13, textColor=colors.HexColor(INK),
            spaceAfter=5
        ),
        "small": ParagraphStyle(
            "small", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=7.7, leading=10.5, textColor=colors.HexColor(MUTED)
        ),
        "metric": ParagraphStyle(
            "metric", parent=styles["BodyText"], fontName="Helvetica-Bold",
            fontSize=14, leading=17, textColor=colors.HexColor(NAVY),
            alignment=TA_CENTER
        ),
        "metric_label": ParagraphStyle(
            "metric_label", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=7.5, leading=9, textColor=colors.HexColor(MUTED),
            alignment=TA_CENTER
        ),
    }


def _pdf_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor(NAVY))
    canvas.rect(0, height - 8 * mm, width, 8 * mm, stroke=0, fill=1)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(colors.white)
    canvas.drawString(18 * mm, height - 5.2 * mm, "HATH HACKERS  •  AI DATA INTELLIGENCE")
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor(MUTED))
    canvas.drawString(18 * mm, 9 * mm, "Confidential analytics report")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _metric_table(items, styles, widths=None):
    cells = []
    for label, value in items:
        cells.append([
            Paragraph(_safe_text(value), styles["metric"]),
            Paragraph(_safe_text(label), styles["metric_label"])
        ])
    row = []
    for cell in cells:
        # ReportLab Table expects a list of rows. Passing the two Paragraphs
        # directly makes ReportLab try to iterate a Paragraph object, which
        # causes: "Paragraph object is not iterable" during PDF generation.
        inner = Table([[cell[0]], [cell[1]]], colWidths=[(widths[0] if widths else 36) * mm])
        inner.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        row.append(inner)
    table = Table([row], colWidths=widths or [40 * mm] * len(items))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(SOFT)),
        ("BOX", (0, 0), (-1, -1), .6, colors.HexColor(LINE)),
        ("INNERGRID", (0, 0), (-1, -1), .6, colors.HexColor(LINE)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def _styled_table(data, col_widths, header_bg=NAVY, font_size=7.7):
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 2),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor(INK)),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor(LINE)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(SOFT)]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def make_pdf(df, filenames, datasets):
    """Create a polished, board-ready business analytics PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=17 * mm, leftMargin=17 * mm,
        topMargin=17 * mm, bottomMargin=16 * mm,
        title="HATH HACKERS | Executive Analytics Report",
        author="HATH HACKERS AI Data Intelligence"
    )
    styles = _report_styles()
    p, measure, missing_rate = _report_metrics(df)
    generated = datetime.datetime.now()

    story = []

    # Cover
    story += [
        Spacer(1, 28 * mm),
        Paragraph("HATH HACKERS", styles["cover_sub"]),
        Paragraph("Executive Analytics<br/>Report", styles["cover_title"]),
        Paragraph(
            "Decision-ready business intelligence generated from the uploaded datasets.",
            styles["cover_sub"]
        ),
        Spacer(1, 10 * mm),
    ]
    cover_meta = [
        ["REPORT DATE", generated.strftime("%d %b %Y, %H:%M")],
        ["DATASETS", str(len(datasets))],
        ["PRIMARY MEASURE", str(measure or "Not detected")],
    ]
    cover_table = _styled_table(
        [["Report metadata", "Value"]] + cover_meta,
        [48 * mm, 112 * mm], header_bg=BLUE
    )
    story += [cover_table, Spacer(1, 13 * mm)]
    story.append(Paragraph(
        "Scope: combined uploaded data across all readable files. "
        "This report separates observed data, statistical evidence and AI-assisted interpretation. "
        "Recommendations should be validated against operational context.",
        styles["body"]
    ))
    story.append(PageBreak())

    # Executive snapshot
    story.append(Paragraph("1. Executive Snapshot", styles["section"]))
    story.append(_metric_table([
        ("Records analysed", _fmt_number(p["rows"])),
        ("Fields", _fmt_number(p["columns"])),
        ("Missing cells", _fmt_number(p["missing"])),
        ("Missing rate", f"{missing_rate:.2f}%"),
    ], styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"The analysis covers {p['rows']:,} records and {p['columns']} fields across "
        f"{len(datasets)} uploaded dataset(s). The primary numeric measure detected for "
        f"business analysis is <b>{_safe_text(measure or 'not detected')}</b>.",
        styles["body"]
    ))

    # Data coverage and quality
    story.append(Paragraph("2. Data Coverage & Quality", styles["section"]))
    file_rows = [["Source file", "Rows", "Columns", "Missing cells"]]
    for name, data in datasets.items():
        file_rows.append([
            Paragraph(_safe_text(name), styles["small"]),
            f"{len(data):,}",
            f"{len(data.columns):,}",
            f"{int(data.isna().sum().sum()):,}",
        ])
    story.append(_styled_table(file_rows, [74 * mm, 25 * mm, 28 * mm, 35 * mm]))
    story.append(Spacer(1, 7))
    quality_rows = [
        ["Quality indicator", "Result", "Interpretation"],
        ["Missing cells", f"{p['missing']:,}", "Null / unavailable values in the combined dataset"],
        ["Missing rate", f"{missing_rate:.2f}%", "Share of all dataset cells that are missing"],
        ["Duplicate rows", f"{p['duplicate']:,}", "Exact duplicate records detected"],
        ["Numeric fields", f"{len(p['numeric']):,}", "Fields available for quantitative analysis"],
        ["Categorical fields", f"{len(p['categorical']):,}", "Fields available for segmentation"],
        ["Date fields", f"{len(p['dates']):,}", "Fields available for time-based analysis"],
    ]
    story.append(_styled_table(quality_rows, [45 * mm, 31 * mm, 86 * mm], header_bg=TEAL))

    # Statistical profile
    story.append(Paragraph("3. Statistical Profile", styles["section"]))
    if measure:
        d = descriptive(df, measure)
        if d:
            stat_rows = [["Statistic", "Value"]]
            for key, value in d.items():
                stat_rows.append([key.replace("_", " ").title(), _fmt_number(value)])
            story.append(Paragraph(
                f"Primary measure: <b>{_safe_text(measure)}</b>", styles["body"]
            ))
            story.append(_styled_table(stat_rows, [75 * mm, 87 * mm], header_bg=BLUE))
            try:
                outliers, _ = zscore_outliers(df, measure)
                story.append(Spacer(1, 5))
                story.append(Paragraph(
                    f"Z-score screening identifies {outliers:,} potential extreme observations "
                    f"(absolute z-score > 3). This is a screening signal, not a definitive anomaly label.",
                    styles["small"]
                ))
            except Exception:
                pass
    else:
        story.append(Paragraph(
            "No suitable numeric measure was detected automatically. Statistical profiling "
            "requires at least one usable numeric field.",
            styles["body"]
        ))

    # Charts
    story.append(PageBreak())
    story.append(Paragraph("4. Business Visual Analysis", styles["section"]))
    story.append(Paragraph(
        "The visual section focuses on trend, concentration, relationship and distribution patterns "
        "generated from the combined dataset.",
        styles["body"]
    ))
    try:
        from backend.chart_engine import auto_charts
        charts = auto_charts(df)
    except Exception:
        charts = []

    chart_count = 0
    for name, fig in charts:
        if chart_count and chart_count % 2 == 0:
            story.append(PageBreak())
        story.append(Paragraph(_safe_text(name), styles["subsection"]))
        try:
            title = getattr(getattr(fig, "layout", None), "title", None)
            title_text = getattr(title, "text", "") if title else ""
            if title_text:
                story.append(Paragraph(_safe_text(title_text), styles["small"]))
            png = fig.to_image(format="png", width=1200, height=600, scale=1)
            story.append(Image(io.BytesIO(png), width=176 * mm, height=88 * mm))
            chart_count += 1
        except Exception:
            story.append(Paragraph(
                "Chart image could not be embedded in the PDF. The interactive chart remains available in the application.",
                styles["small"]
            ))
    if not chart_count:
        story.append(Paragraph("No automatic charts were available for this dataset.", styles["body"]))

    # AI executive analysis
    story.append(PageBreak())
    story.append(Paragraph("5. Executive Intelligence", styles["section"]))
    ai = executive_insights(df)
    ai_lines = _clean_ai_markdown(ai)
    if ai_lines:
        for line in ai_lines:
            if line.startswith("• "):
                story.append(Paragraph(_safe_text(line), styles["body"]))
            else:
                story.append(Paragraph(_safe_text(line), styles["body"]))
    else:
        story.append(Paragraph(
            "AI executive analysis was not generated for this session.",
            styles["body"]
        ))

    # Forecast
    story.append(Paragraph("6. Forecast & Forward View", styles["section"]))
    forecast = st.session_state.get("forecast_table")
    if forecast is not None and len(forecast):
        columns = [str(c) for c in forecast.columns]
        view = forecast.head(24).copy()
        fr = [[_safe_text(c) for c in columns]]
        for row in view.itertuples(index=False, name=None):
            fr.append([_safe_text(v) for v in row])
        widths = [162 * mm / max(len(columns), 1)] * len(columns)
        story.append(Paragraph(
            "The table below reflects the forecast currently generated in the application session.",
            styles["body"]
        ))
        story.append(_styled_table(fr, widths, header_bg=AMBER))
    else:
        story.append(Paragraph(
            "No forecast was generated in this session. A forecast requires a suitable date field "
            "and numeric measure.",
            styles["body"]
        ))

    # Q&A appendix
    history = st.session_state.get("ai_history", [])
    story.append(Paragraph("7. Analyst Q&A Appendix", styles["section"]))
    if history:
        for i, (question, answer) in enumerate(history, 1):
            story.append(Paragraph(f"Q{i}. {_safe_text(question)}", styles["subsection"]))
            story.append(Paragraph(_safe_text(answer).replace("\n", "<br/>"), styles["body"]))
    else:
        story.append(Paragraph(
            "No analyst questions were recorded during this session.",
            styles["body"]
        ))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Methodology note: automated insights are based only on the supplied dataset and available "
        "session outputs. Statistical association does not establish causation. Validate material "
        "business decisions with domain knowledge and source-system controls.",
        styles["small"]
    ))

    doc.build(story, onFirstPage=_pdf_header_footer, onLaterPages=_pdf_header_footer)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Streamlit report workspace
# ---------------------------------------------------------------------------

def _kpi_card(label, value, detail=""):
    st.markdown(
        f"""
        <div class="report-kpi">
            <div class="report-kpi-label">{html.escape(label)}</div>
            <div class="report-kpi-value">{html.escape(str(value))}</div>
            <div class="report-kpi-detail">{html.escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _inject_report_css():
    st.markdown(
        """
        <style>
        .report-hero {
            padding: 28px 30px;
            border-radius: 20px;
            background: linear-gradient(135deg, #0B1730 0%, #162A4A 55%, #0F9F9A 160%);
            border: 1px solid rgba(37,99,235,.35);
            box-shadow: 0 18px 45px rgba(8,23,48,.18);
            margin-bottom: 18px;
        }
        .report-hero .eyebrow {
            color: #8FB7FF;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .report-hero h1 {
            color: white !important;
            margin: 6px 0 4px;
            font-size: 34px;
            text-shadow: none;
        }
        .report-hero p {
            color: #D8E7FF !important;
            margin: 0;
            max-width: 820px;
        }
        .report-kpi {
            background: rgba(255,255,255,.96);
            border: 1px solid #DCE4EE;
            border-radius: 16px;
            padding: 17px 18px;
            min-height: 112px;
            box-shadow: 0 8px 25px rgba(15,23,42,.06);
        }
        .report-kpi-label {
            color: #64748B;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .6px;
        }
        .report-kpi-value {
            color: #0B1730;
            font-size: 26px;
            line-height: 1.15;
            font-weight: 850;
            margin-top: 7px;
        }
        .report-kpi-detail {
            color: #94A3B8;
            font-size: 11px;
            margin-top: 5px;
        }
        .report-section {
            background: rgba(255,255,255,.96);
            border: 1px solid #DCE4EE;
            border-radius: 18px;
            padding: 20px 22px;
            margin-top: 18px;
            box-shadow: 0 8px 25px rgba(15,23,42,.045);
        }
        .report-section h3 {
            color: #0B1730 !important;
            margin: 0 0 5px;
            text-shadow: none;
        }
        .report-section p {
            color: #64748B !important;
            margin: 0;
        }
        .report-pill {
            display: inline-block;
            background: #EEF4FF;
            color: #2563EB;
            border: 1px solid #D6E3FF;
            border-radius: 999px;
            padding: 5px 10px;
            margin: 4px 5px 0 0;
            font-size: 11px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_reports():
    _inject_report_css()

    data = st.session_state.get("data")
    if data is None or data.empty:
        st.markdown(
            """
            <div class="report-hero">
                <div class="eyebrow">Executive Reporting</div>
                <h1>Business Report Center</h1>
                <p>Upload a dataset to build a decision-ready analytics report.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.info("Upload CSV or Excel data from the sidebar to activate report generation.")
        return

    datasets = st.session_state.get("datasets", {})
    filenames = st.session_state.get(
        "dataset_names",
        list(datasets) if datasets else [st.session_state.get("dataset_name", "Dataset")]
    )
    p, measure, missing_rate = _report_metrics(data)

    st.markdown(
        f"""
        <div class="report-hero">
            <div class="eyebrow">HATH HACKERS · Enterprise Analytics</div>
            <h1>Business Report Center</h1>
            <p>Generate a board-ready report with executive KPIs, data quality, statistical evidence,
            business visuals, AI-assisted intelligence, forecast context and analyst Q&A.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        _kpi_card("Records", f"{p['rows']:,}", "combined rows analysed")
    with k2:
        _kpi_card("Fields", f"{p['columns']:,}", "available columns")
    with k3:
        _kpi_card("Data quality", f"{100 - missing_rate:.1f}%", "non-missing cell rate")
    with k4:
        _kpi_card("Primary measure", measure or "Not detected", "automatic analysis field")

    st.markdown(
        """
        <div class="report-section">
            <h3>Report scope</h3>
            <p>The report uses the combined dataset and all readable uploaded files. The PDF intentionally
            focuses on business findings rather than application navigation or internal chart inventory.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### Included in the report")
        items = [
            ("Executive snapshot", "Management-ready KPIs and scope"),
            ("Data quality", "Missingness, duplicates and field coverage"),
            ("Statistical profile", "Distribution, summary statistics and outlier screening"),
            ("Business visuals", "Automatic trend, mix, relationship and distribution charts"),
            ("Executive intelligence", "AI-assisted findings, implications and recommendations"),
            ("Forecast", "Current session forecast when available"),
            ("Analyst Q&A", "Questions and answers captured in this session"),
        ]
        for title, desc in items:
            st.markdown(
                f"<span class='report-pill'>{html.escape(title)}</span> "
                f"<span style='color:#64748B;font-size:12px'>{html.escape(desc)}</span>",
                unsafe_allow_html=True
            )

    with right:
        st.markdown("### Source coverage")
        coverage = pd.DataFrame([
            {
                "File": name,
                "Rows": len(frame),
                "Columns": len(frame.columns),
            }
            for name, frame in datasets.items()
        ])
        if not coverage.empty:
            st.dataframe(coverage, use_container_width=True, hide_index=True)
        else:
            st.write("Combined dataset only")

    st.markdown("### Generate report")
    c1, c2, c3 = st.columns([1, 1, 1.4])
    with c1:
        if st.button("Generate / Refresh PDF", type="primary", use_container_width=True):
            with st.spinner("Building executive business report..."):
                try:
                    st.session_state.report_pdf = make_pdf(data, filenames, datasets)
                    st.session_state.report_generated_at = datetime.datetime.now()
                    st.success("Report generated successfully.")
                except Exception as exc:
                    st.error(f"Report generation failed: {exc}")
    with c2:
        if st.session_state.get("report_pdf"):
            st.download_button(
                "Download PDF",
                st.session_state.report_pdf,
                "HATH_HACKERS_Executive_Business_Report.pdf",
                "application/pdf",
                use_container_width=True
            )
    with c3:
        generated_at = st.session_state.get("report_generated_at")
        st.caption(
            f"Last generated: {generated_at:%d %b %Y, %H:%M}"
            if generated_at else
            "No report generated yet in this session."
        )

    if st.session_state.get("report_pdf"):
        st.markdown(
            """
            <div class="report-section">
                <h3>Report ready</h3>
                <p>Your PDF contains the executive snapshot, data coverage, statistical analysis,
                business visuals, AI intelligence, forecast context and analyst Q&A.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
