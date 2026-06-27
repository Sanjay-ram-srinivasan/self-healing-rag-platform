import os
import json
import logging
from datetime import datetime
from backend.analytics import load_stats, resolve_analytics_period, filter_queries_by_timestamp, summarize_analytics, build_analytics_report

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_pdf")

def test_generate_pdf():
    selected_range = "all"
    start_date = None
    end_date = None
    total_documents = 5
    vector_store_mb = 1.2
    
    # Load stats
    stats = load_stats()
    queries = stats.get("queries", [])
    print(f"Loaded {len(queries)} total queries.")
    
    # Resolve range
    start_dt, end_dt = resolve_analytics_period(selected_range, start_date, end_date)
    filtered_queries = filter_queries_by_timestamp(queries, start_dt, end_dt)
    print(f"Filtered queries: {len(filtered_queries)}.")
    
    stats["queries"] = filtered_queries
    raw_data = summarize_analytics(
        stats=stats,
        total_documents=total_documents,
        vector_store_mb=vector_store_mb,
        start_dt=start_dt,
        end_dt=end_dt,
        selected_range=selected_range,
    )
    report = build_analytics_report(raw_data)
    report["documents_indexed"] = total_documents
    report["vector_store_mb"] = vector_store_mb
    report["status"] = raw_data.get("status", "healthy")
    report["generated_at"] = datetime.utcnow().isoformat() + "Z"
    report["charts_summary"] = {
        "confidence_trend": [
            {"date": item.get("date"), "average_confidence": item.get("average_confidence", 0)}
            for item in raw_data.get("history", [])
        ],
        "faithfulness_trend": [
            {"date": item.get("date"), "average_faithfulness": item.get("average_faithfulness", 0)}
            for item in raw_data.get("history", [])
        ],
        "retry_trend": [
            {"date": item.get("date"), "retries": item.get("retries", 0)}
            for item in raw_data.get("history", [])
        ],
        "overview": [
            {"name": "Total Queries", "value": raw_data.get("total_queries", 0)},
            {"name": "Retried Queries", "value": raw_data.get("retry_count", 0)},
            {"name": "Reliable Answers", "value": raw_data.get("reliable_count", 0)},
            {"name": "Hallucinations", "value": raw_data.get("hallucination_count", 0)},
        ],
    }

    # PDF generation logic
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError as exc:
        print(f"ReportLab import failed: {exc}")
        return

    tmp_path = "test_analytics_report.pdf"
    try:
        c = rl_canvas.Canvas(tmp_path, pagesize=letter)
        page_width, page_height = letter

        def _new_page_if_needed(y_pos, min_y=80):
            if y_pos < min_y:
                c.showPage()
                return page_height - 60
            return y_pos

        def _section_header(y_pos, title):
            y_pos = _new_page_if_needed(y_pos, 120)
            c.setFillColor(colors.HexColor("#F5DFD2"))
            c.rect(40, y_pos - 6, page_width - 80, 22, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#6A2A05"))
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y_pos + 4, title)
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 10)
            return y_pos - 26

        def _kv_row(y_pos, label, value, row_bg=False):
            y_pos = _new_page_if_needed(y_pos)
            if row_bg:
                c.setFillColor(colors.HexColor("#FDF5F2"))
                c.rect(40, y_pos - 4, page_width - 80, 16, fill=1, stroke=0)
                c.setFillColor(colors.black)
            c.setFont("Helvetica", 10)
            c.drawString(55, y_pos, str(label))
            c.drawRightString(page_width - 50, y_pos, str(value))
            return y_pos - 18

        # ── Cover header ───────────────────────────────────────────────────
        c.setFillColor(colors.HexColor("#C84B2F"))
        c.rect(0, page_height - 90, page_width, 90, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(50, page_height - 48, "Self-Healing RAG Platform")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, page_height - 68, "Analytics Report")
        c.setFont("Helvetica", 10)
        c.drawString(50, page_height - 84, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

        y = page_height - 110

        # ── Date Range ────────────────────────────────────────────────────
        y = _section_header(y, "Date Range")
        date_range = report.get("date_range", {})
        row_bg = False
        for lbl, val in [
            ("Range", date_range.get("range", selected_range)),
            ("Start Date", (date_range.get("start_date") or "N/A")[:10]),
            ("End Date", (date_range.get("end_date") or "N/A")[:10]),
        ]:
            y = _kv_row(y, lbl, val, row_bg)
            row_bg = not row_bg
        y -= 10

        # ── Summary ───────────────────────────────────────────────────────
        y = _section_header(y, "Summary")
        row_bg = False
        for lbl, val in [
            ("Total Queries", report.get("total_queries", 0)),
            ("Documents Indexed", total_documents),
            ("Vector Store Size (MB)", vector_store_mb),
            ("System Status", report.get("status", "healthy").title()),
        ]:
            y = _kv_row(y, lbl, val, row_bg)
            row_bg = not row_bg
        y -= 10

        # ── Confidence Metrics ────────────────────────────────────────────
        y = _section_header(y, "Confidence Metrics")
        conf = report.get("confidence_metrics", {})
        row_bg = False
        y = _kv_row(y, "Average Confidence", f"{conf.get('average_confidence', 0):.1f}%", row_bg)
        y -= 10

        # ── Faithfulness Metrics ──────────────────────────────────────────
        y = _section_header(y, "Faithfulness Metrics")
        faith = report.get("faithfulness_metrics", {})
        row_bg = False
        for lbl, key in [
            ("Average Faithfulness", "average_faithfulness"),
            ("Average Relevance", "average_relevance"),
            ("Average Precision", "average_precision"),
            ("Average Recall", "average_recall"),
        ]:
            y = _kv_row(y, lbl, f"{faith.get(key, 0):.1f}%", row_bg)
            row_bg = not row_bg
        y -= 10

        # ── Hallucination Rate ────────────────────────────────────────────
        y = _section_header(y, "Hallucination Rate")
        hall = report.get("hallucination_rate", {})
        row_bg = False
        for lbl, val in [
            ("Hallucination Rate", f"{hall.get('rate', 0):.1f}%"),
            ("Hallucinated Queries", hall.get("count", 0)),
            ("Reliable Answers", hall.get("reliable_count", 0)),
        ]:
            y = _kv_row(y, lbl, val, row_bg)
            row_bg = not row_bg
        y -= 10

        # ── Retry Statistics ──────────────────────────────────────────────
        y = _section_header(y, "Retry Statistics")
        retry = report.get("retry_statistics", {})
        row_bg = False
        for lbl, val in [
            ("Retry Rate", f"{retry.get('retry_rate', 0):.1f}%"),
            ("Total Retried Queries", retry.get("retry_count", 0)),
        ]:
            y = _kv_row(y, lbl, val, row_bg)
            row_bg = not row_bg
        y -= 10

        # ── Charts Summary ────────────────────────────────────────────────
        charts = report.get("charts_summary", {})
        overview = charts.get("overview", [])
        if overview:
            y = _section_header(y, "Charts Summary — Overview")
            row_bg = False
            for item in overview:
                y = _kv_row(y, item.get("name", ""), item.get("value", 0), row_bg)
                row_bg = not row_bg
            y -= 10

        # ── Most Queried Documents ────────────────────────────────────────
        top_docs = report.get("most_queried_documents", [])
        if top_docs:
            y = _section_header(y, "Most Queried Documents")
            row_bg = False
            for item in top_docs[:10]:
                y = _kv_row(y, item.get("document", ""), f"{item.get('queries', 0)} queries", row_bg)
                row_bg = not row_bg
            y -= 10

        # ── Footer ────────────────────────────────────────────────────────
        c.setFillColor(colors.HexColor("#6A4034"))
        c.setFont("Helvetica", 8)
        c.drawCentredString(page_width / 2, 30, "Self-Healing RAG Platform  |  Confidential Analytics Report")

        c.save()
        print("PDF generated successfully and saved to test_analytics_report.pdf")
    except Exception as e:
        print("PDF generation failed with exception:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generate_pdf()
