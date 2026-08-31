import html
import os

import gradio as gr
import requests


API_URL = os.getenv(
    "API_URL",
    "http://api:8001/api/v1/investigations",
)

CASE_CATALOGUE = {
    "CASE-001": "Duplicate 5,000 ETB transfers — balance discrepancy",
    "CASE-002": "Failed 10,000 ETB transfer — possible deduction",
    "CASE-003": "Reversed transfer — was balance restored?",
    "CASE-004": "Incoming 5,000 ETB — confirm credit",
    "CASE-005": "Outgoing 2,000 ETB — confirm debit",
    "CASE-006": "Incoming 2,000 ETB — verify credit",
    "CASE-007": "Outgoing 1,500 ETB — confirm deduction",
    "CASE-008": "Incoming 1,500 ETB — confirm credit",
    "CASE-009": "Two 5,000 ETB transfers within minutes — investigate",
    "CASE-010": "Failed 10,000 ETB — was account permanently debited?",
    "CASE-011": "Failed incoming 10,000 ETB — was anything credited?",
    "CASE-012": "Incoming 2,000 ETB — verify balance change",
    "CASE-013": "Outgoing 2,000 ETB — verify debit",
    "CASE-014": "Reversed outgoing 1,000 ETB — check debit and restoration",
    "CASE-015": "Reversed incoming 1,000 ETB — verify balance impact",
    "CASE-016": "Outgoing 2,500 ETB — confirm status and deduction",
    "CASE-017": "Incoming 2,500 ETB — confirm credit",
    "CASE-018": "Multi-transaction review — full account activity",
    "CASE-019": "Multi-transaction review — incoming, outgoing, reversed",
    "CASE-020": "Duplicate 5,000 ETB transfers — were both processed?",
}

CONFIDENCE_BADGE = {
    "HIGH":   ("#16a34a", "#dcfce7", "HIGH"),
    "MEDIUM": ("#d97706", "#fef3c7", "MEDIUM"),
    "LOW":    ("#dc2626", "#fee2e2", "LOW"),
}

CSS = """
/* Reset & base */
*, *::before, *::after { box-sizing: border-box; }

.gradio-container {
    max-width: 1080px !important;
    margin: 0 auto !important;
    font-family: 'Inter', system-ui, sans-serif;
}

/* ── Header ─────────────────────────────────────────── */
.hdr {
    background: linear-gradient(160deg, #0f172a 0%, #1e3a5f 100%);
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.hdr-eyebrow {
    display: inline-block;
    margin-bottom: 10px;
    padding: 3px 10px;
    background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 100px;
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.hdr h1 {
    margin: 0 0 8px;
    font-size: 22px;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.3;
}
.hdr p {
    margin: 0;
    font-size: 13.5px;
    color: #94a3b8;
    line-height: 1.6;
    max-width: 620px;
}

/* ── Cards ───────────────────────────────────────────── */
.c-base {
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 14px;
    line-height: 1;
}
.c-white  { background: #ffffff; border: 1px solid #e2e8f0; }
.c-blue   { background: #eff6ff; border: 1px solid #bfdbfe; }
.c-amber  { background: #fffbeb; border: 1px solid #fcd34d; }
.c-red    { background: #fef2f2; border: 1px solid #fca5a5; }

/* ── Section label ───────────────────────────────────── */
.slabel {
    display: block;
    margin-bottom: 10px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: .09em;
    text-transform: uppercase;
    color: #94a3b8;
}

/* ── Summary table ───────────────────────────────────── */
.stbl { width: 100%; border-collapse: collapse; }
.stbl td { padding: 5px 0; vertical-align: middle; }
.stbl .k { width: 110px; font-size: 13px; color: #64748b; }
.stbl .v { font-size: 14px; color: #0f172a; font-weight: 600; }

/* ── Confidence badge ────────────────────────────────── */
.conf {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .04em;
}

/* ── Status pill ─────────────────────────────────────── */
.spill {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    background: #dbeafe;
    color: #1d4ed8;
}

/* ── Complaint row ───────────────────────────────────── */
.complaint {
    margin: 0 0 14px;
    padding: 10px 14px;
    background: #f8fafc;
    border-left: 3px solid #94a3b8;
    border-radius: 0 6px 6px 0;
    font-size: 13.5px;
    color: #475569;
    font-style: italic;
    line-height: 1.5;
}

/* ── Finding card ────────────────────────────────────── */
.finding {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.finding-title {
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 10px;
    line-height: 1.5;
}
.evlist {
    list-style: none;
    margin: 0;
    padding: 0;
}
.evlist li {
    position: relative;
    padding: 3px 0 3px 16px;
    font-size: 13px;
    color: #475569;
    line-height: 1.55;
}
.evlist li::before {
    content: "›";
    position: absolute;
    left: 2px;
    color: #3b82f6;
    font-weight: 700;
}

/* ── Body text ───────────────────────────────────────── */
.body-text {
    margin: 0;
    font-size: 14px;
    color: #1e293b;
    line-height: 1.65;
}
.rec-text {
    margin: 0;
    font-size: 13.5px;
    color: #1e40af;
    line-height: 1.6;
    font-style: italic;
}
.note-text {
    margin: 8px 0 0;
    font-size: 12px;
    color: #60a5fa;
}

/* ── Human review ────────────────────────────────────── */
.review-title {
    margin: 0 0 6px;
    font-size: 14px;
    font-weight: 700;
    color: #92400e;
}
.review-body {
    margin: 0;
    font-size: 13.5px;
    color: #78350f;
    line-height: 1.6;
}

/* ── How it works ────────────────────────────────────── */
.how-box {
    margin-top: 20px;
    padding: 16px 18px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}
.how-title {
    margin: 0 0 10px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: #64748b;
}
.how-list {
    margin: 0;
    padding-left: 18px;
    color: #64748b;
    font-size: 13px;
    line-height: 1.85;
}

/* ── Footer ──────────────────────────────────────────── */
.footer {
    margin-top: 20px;
    padding-top: 14px;
    border-top: 1px solid #f1f5f9;
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
    line-height: 1.6;
}

/* ── Ready state ─────────────────────────────────────── */
.ready-title {
    margin: 0 0 8px;
    font-size: 15px;
    font-weight: 600;
    color: #0f172a;
}
.ready-body {
    margin: 0;
    font-size: 13.5px;
    color: #64748b;
    line-height: 1.6;
}
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _conf_badge(level: str) -> str:
    level = (level or "UNKNOWN").upper()
    color, bg = CONFIDENCE_BADGE.get(level, ("#64748b", "#f1f5f9"))[:2]
    return (
        f'<span class="conf" '
        f'style="background:{bg};color:{color};">'
        f'{html.escape(level)}</span>'
    )


def _error(title: str, body: str) -> str:
    return (
        f'<div class="c-base c-red">'
        f'<p style="margin:0 0 6px;font-weight:600;font-size:14px;color:#991b1b;">{html.escape(title)}</p>'
        f'<p style="margin:0;font-size:13.5px;color:#7f1d1d;line-height:1.6;">{html.escape(body)}</p>'
        f'</div>'
    )


# ── Main handler ──────────────────────────────────────────────────────────────

def investigate(case_id: str) -> str:
    case_id = (case_id or "").strip().upper()

    if not case_id:
        return _error(
            "Case ID required",
            "Enter an investigation case ID or select one from the catalogue.",
        )

    try:
        response = requests.post(
            API_URL,
            json={"case_id": case_id},
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()

    except requests.exceptions.Timeout:
        return _error(
            "Investigation timed out",
            "The request exceeded the allowed time. Please try again.",
        )
    except requests.exceptions.HTTPError:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        return _error("Investigation failed", str(detail))
    except requests.exceptions.RequestException:
        return _error(
            "Connection error",
            "Could not reach the investigation service. Verify the API is running.",
        )

    # ── Parse ─────────────────────────────────────────────────────────
    findings       = result.get("findings", [])
    confidence     = result.get("confidence", "UNKNOWN")
    status         = result.get("status", "PENDING_REVIEW")
    conclusion     = result.get("conclusion", "")
    recommendation = result.get("recommendation", "")
    complaint      = CASE_CATALOGUE.get(case_id, "")

    # ── Complaint ─────────────────────────────────────────────────────
    complaint_html = (
        f'<p class="complaint">"{html.escape(complaint)}"</p>'
        if complaint else ""
    )

    # ── Summary card ──────────────────────────────────────────────────
    summary = f"""
<div class="c-base c-white">
  <span class="slabel">Investigation Summary</span>
  {complaint_html}
  <table class="stbl">
    <tr><td class="k">Case</td>
        <td class="v">{html.escape(case_id)}</td></tr>
    <tr><td class="k">Status</td>
        <td class="v"><span class="spill">{html.escape(status)}</span></td></tr>
    <tr><td class="k">Confidence</td>
        <td class="v">{_conf_badge(confidence)}</td></tr>
    <tr><td class="k">Findings</td>
        <td class="v">{len(findings)}</td></tr>
  </table>
</div>"""

    # ── Findings ──────────────────────────────────────────────────────
    findings_html = ""
    for i, f in enumerate(findings, 1):
        desc = html.escape(f.get("description", "No description."))
        items = "".join(
            f'<li>{html.escape(str(e))}</li>'
            for e in f.get("evidence", [])
        ) or '<li style="color:#94a3b8;">No supporting evidence provided.</li>'
        findings_html += f"""
<div class="finding">
  <div class="finding-title">Finding {i} — {desc}</div>
  <ul class="evlist">{items}</ul>
</div>"""

    if not findings_html:
        findings_html = '<p style="color:#94a3b8;font-size:13.5px;">No findings reported.</p>'

    findings_section = f"""
<div style="margin-bottom:14px;">
  <span class="slabel">Evidence-Based Findings</span>
  {findings_html}
</div>"""

    # ── Conclusion ────────────────────────────────────────────────────
    conclusion_card = f"""
<div class="c-base c-white">
  <span class="slabel">Conclusion</span>
  <p class="body-text">{html.escape(conclusion)}</p>
</div>"""

    # ── Recommendation ────────────────────────────────────────────────
    recommendation_card = f"""
<div class="c-base c-blue">
  <span class="slabel">Advisory Recommendation</span>
  <p class="rec-text">{html.escape(recommendation)}</p>
  <p class="note-text">Advisory only — no financial action is executed automatically.</p>
</div>"""

    # ── Human review ──────────────────────────────────────────────────
    review_card = """
<div class="c-base c-amber">
  <p class="review-title">🔎 Awaiting Human Review</p>
  <p class="review-body">
    This investigation is pending review by an authorized operations officer.
    No refund, reversal, balance adjustment, or other consequential action
    is executed automatically by this system.
  </p>
</div>"""

    # ── Footer ────────────────────────────────────────────────────────
    footer = """
<div class="footer">
  Financial Transaction Investigation Agent &nbsp;·&nbsp;
  Evidence gathered via controlled MCP capabilities &nbsp;·&nbsp;
  All consequential actions require human authorization
</div>"""

    return summary + findings_section + conclusion_card + recommendation_card + review_card + footer


def _set_case(selection: str) -> str:
    return selection.split(" — ", 1)[0] if selection else ""


# ── UI ────────────────────────────────────────────────────────────────────────

CASE_CHOICES = [f"{cid} — {desc}" for cid, desc in CASE_CATALOGUE.items()]

with gr.Blocks(
    title="Financial Investigation Agent",
) as demo:

    gr.HTML("""
<div class="hdr">
  <h1>Financial Transaction Investigation Agent</h1>
  <p>
    Evidence-driven investigation for financial transaction complaints.
    The agent collects customer, account, transaction, ledger, and balance
    evidence through controlled MCP capabilities and returns a structured
    result for mandatory human review.
  </p>
</div>""")

    with gr.Row(equal_height=False):

        with gr.Column(scale=2):
            case_input = gr.Textbox(
                label="Investigation Case ID",
                placeholder="e.g. CASE-001",
            )
            run_btn = gr.Button(
                "Run Investigation",
                variant="primary",
                size="lg",
            )
            catalogue = gr.Dropdown(
                label="Or select from catalogue",
                choices=CASE_CHOICES,
                value=None,
            )
            gr.HTML("""
<div class="how-box">
  <p class="how-title">Agent Workflow</p>
  <ol class="how-list">
    <li>Retrieve the investigation case</li>
    <li>Collect evidence via MCP tools</li>
    <li>Run deterministic balance comparison</li>
    <li>LLM correlates evidence into findings</li>
    <li>Return structured result for human review</li>
  </ol>
</div>""")

        with gr.Column(scale=3):
            result_output = gr.HTML(value="""
<div class="c-base c-white">
  <p class="ready-title">Ready for Investigation</p>
  <p class="ready-body">
    Enter a case ID or select one from the catalogue,
    then click <strong>Run Investigation</strong>.<br><br>
    The agent will gather evidence and return findings
    for human review.
  </p>
</div>""")

    run_btn.click(fn=investigate, inputs=case_input, outputs=result_output, show_progress="full")
    case_input.submit(fn=investigate, inputs=case_input, outputs=result_output, show_progress="full")
    catalogue.change(fn=_set_case, inputs=catalogue, outputs=case_input)

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    theme=gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        neutral_hue=gr.themes.colors.slate,
        font=gr.themes.GoogleFont("Inter"),
    ),
    css=CSS,
)
