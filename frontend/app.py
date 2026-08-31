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
    "HIGH": ("#15803d", "#dcfce7"),
    "MEDIUM": ("#b45309", "#fef3c7"),
    "LOW": ("#b91c1c", "#fee2e2"),
}


CSS = """
/* =========================================================
   BASE
   ========================================================= */

*,
*::before,
*::after {
    box-sizing: border-box;
}

body {
    background: #f8fafc;
}

.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 28px 24px 40px !important;
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont,
                 "Segoe UI", sans-serif !important;
}


/* =========================================================
   HEADER
   ========================================================= */

.app-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 18px;
    color: white;
}

.header-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
}

.header-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    color: #bfdbfe;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 9px;
}

.header-eyebrow::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #60a5fa;
}

.app-header h1 {
    margin: 0 0 8px;
    color: #f8fafc;
    font-size: 25px;
    line-height: 1.25;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.app-header p {
    margin: 0;
    max-width: 720px;
    color: #cbd5e1;
    font-size: 13.5px;
    line-height: 1.65;
}

.system-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 18px;
}

.system-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 10px;
    border: 1px solid rgba(255,255,255,.13);
    background: rgba(255,255,255,.07);
    border-radius: 999px;
    color: #dbeafe;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .05em;
}

.system-badge .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #4ade80;
}


/* =========================================================
   MAIN GRID
   ========================================================= */

.main-grid {
    display: grid;
    grid-template-columns: 330px minmax(0, 1fr);
    gap: 18px;
    align-items: start;
}


/* =========================================================
   PANEL
   ========================================================= */

.panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
}

.panel-title {
    margin: 0 0 4px;
    color: #0f172a;
    font-size: 14px;
    font-weight: 700;
}

.panel-subtitle {
    margin: 0 0 18px;
    color: #64748b;
    font-size: 12px;
    line-height: 1.55;
}


/* =========================================================
   INPUT
   ========================================================= */

.input-label {
    display: block;
    margin-bottom: 7px;
    color: #334155;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .04em;
    text-transform: uppercase;
}

.case-input input {
    height: 44px !important;
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: none !important;
    font-size: 14px !important;
}

.case-input input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,.10) !important;
}

.run-button {
    width: 100% !important;
    margin-top: 10px !important;
    border-radius: 8px !important;
    min-height: 44px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
}


/* =========================================================
   CASE SELECTOR
   ========================================================= */

.selector-label {
    display: block;
    margin: 18px 0 7px;
    color: #64748b;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.case-select {
    margin-bottom: 0 !important;
}

.case-select .wrap {
    border-radius: 8px !important;
}

.case-select input {
    font-size: 13px !important;
}


/* =========================================================
   WORKFLOW
   ========================================================= */

.workflow {
    margin-top: 20px;
    padding-top: 18px;
    border-top: 1px solid #eef2f7;
}

.workflow-title {
    margin: 0 0 14px;
    color: #334155;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .09em;
    text-transform: uppercase;
}

.workflow-step {
    display: flex;
    align-items: flex-start;
    gap: 11px;
    position: relative;
    padding-bottom: 14px;
}

.workflow-step:last-child {
    padding-bottom: 0;
}

.workflow-step:not(:last-child)::after {
    content: "";
    position: absolute;
    left: 10px;
    top: 22px;
    bottom: 1px;
    width: 1px;
    background: #dbe3ec;
}

.step-number {
    position: relative;
    z-index: 1;
    flex: 0 0 21px;
    width: 21px;
    height: 21px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #2563eb;
    font-size: 9px;
    font-weight: 800;
}

.step-content strong {
    display: block;
    margin-top: 1px;
    color: #334155;
    font-size: 12px;
    font-weight: 600;
}

.step-content span {
    display: block;
    margin-top: 2px;
    color: #94a3b8;
    font-size: 10.5px;
    line-height: 1.4;
}


/* =========================================================
   READY PANEL
   ========================================================= */

.ready-panel {
    min-height: 360px;
}

.ready-state {
    min-height: 320px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 20px 28px;
}

.ready-icon {
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: #eff6ff;
    border: 1px solid #dbeafe;
    color: #2563eb;
    font-size: 18px;
    margin-bottom: 16px;
}

.ready-state h2 {
    margin: 0 0 7px;
    color: #0f172a;
    font-size: 19px;
    font-weight: 700;
}

.ready-state p {
    max-width: 560px;
    margin: 0;
    color: #64748b;
    font-size: 13px;
    line-height: 1.65;
}

.ready-hint {
    margin-top: 18px !important;
    padding: 11px 13px;
    border-left: 3px solid #60a5fa;
    background: #f8fafc;
    border-radius: 0 7px 7px 0;
    color: #475569 !important;
    font-size: 12px !important;
}


/* =========================================================
   RESULT
   ========================================================= */

.result-wrapper {
    width: 100%;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 18px;
    padding-bottom: 17px;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 17px;
}

.result-case {
    margin: 0 0 5px;
    color: #0f172a;
    font-size: 19px;
    font-weight: 700;
}

.result-complaint {
    margin: 0;
    color: #64748b;
    font-size: 12.5px;
    line-height: 1.5;
}

.result-badges {
    display: flex;
    gap: 7px;
    flex-shrink: 0;
}

.result-badge {
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 9.5px;
    font-weight: 800;
    letter-spacing: .05em;
    text-transform: uppercase;
}

.status-badge {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #dbeafe;
}

.conf-high {
    background: #dcfce7;
    color: #15803d;
    border: 1px solid #bbf7d0;
}

.conf-medium {
    background: #fef3c7;
    color: #b45309;
    border: 1px solid #fde68a;
}

.conf-low {
    background: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fecaca;
}

.conf-unknown {
    background: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
}


/* =========================================================
   RESULT METRICS
   ========================================================= */

.metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 9px;
    margin-bottom: 18px;
}

.metric {
    padding: 12px 13px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

.metric-label {
    display: block;
    color: #94a3b8;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.metric-value {
    display: block;
    margin-top: 4px;
    color: #0f172a;
    font-size: 14px;
    font-weight: 700;
}


/* =========================================================
   SECTIONS
   ========================================================= */

.result-section {
    margin-bottom: 17px;
}

.section-label {
    display: block;
    margin-bottom: 8px;
    color: #64748b;
    font-size: 9.5px;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
}

.finding {
    margin-bottom: 8px;
    padding: 13px 14px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #3b82f6;
    border-radius: 7px;
}

.finding-title {
    margin-bottom: 7px;
    color: #1e293b;
    font-size: 12.5px;
    font-weight: 700;
    line-height: 1.5;
}

.evidence {
    margin: 0;
    padding: 0;
    list-style: none;
}

.evidence li {
    position: relative;
    padding: 2px 0 2px 14px;
    color: #64748b;
    font-size: 11.5px;
    line-height: 1.55;
}

.evidence li::before {
    content: "•";
    position: absolute;
    left: 2px;
    color: #3b82f6;
    font-weight: 800;
}

.empty {
    color: #94a3b8;
    font-size: 12px;
}


/* =========================================================
   CONCLUSION / RECOMMENDATION
   ========================================================= */

.conclusion-box {
    padding: 14px 15px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

.conclusion-text {
    margin: 0;
    color: #334155;
    font-size: 12.5px;
    line-height: 1.65;
}

.recommendation-box {
    padding: 14px 15px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
}

.recommendation-text {
    margin: 0;
    color: #1e40af;
    font-size: 12.5px;
    line-height: 1.65;
}

.advisory-note {
    margin: 8px 0 0;
    color: #60a5fa;
    font-size: 10.5px;
}


/* =========================================================
   HUMAN REVIEW
   ========================================================= */

.review-box {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 14px 15px;
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 8px;
}

.review-icon {
    flex: 0 0 28px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #fef3c7;
    border-radius: 7px;
    color: #b45309;
    font-size: 13px;
}

.review-box h3 {
    margin: 0 0 4px;
    color: #92400e;
    font-size: 12.5px;
    font-weight: 800;
}

.review-box p {
    margin: 0;
    color: #78350f;
    font-size: 11.5px;
    line-height: 1.55;
}


/* =========================================================
   FOOTER
   ========================================================= */

.app-footer {
    margin-top: 16px;
    padding: 12px 0 0;
    border-top: 1px solid #e2e8f0;
    color: #94a3b8;
    font-size: 10px;
    text-align: center;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 850px) {
    .main-grid {
        grid-template-columns: 1fr;
    }

    .result-header {
        flex-direction: column;
    }

    .metrics {
        grid-template-columns: 1fr;
    }
}
"""


def _confidence_class(level: str) -> str:
    level = (level or "UNKNOWN").upper()

    if level == "HIGH":
        return "conf-high"
    if level == "MEDIUM":
        return "conf-medium"
    if level == "LOW":
        return "conf-low"

    return "conf-unknown"


def _error(title: str, body: str) -> str:
    return f"""
    <div class="result-wrapper">
        <div class="review-box"
             style="background:#fef2f2;border-color:#fca5a5;">
            <div class="review-icon"
                 style="background:#fee2e2;color:#b91c1c;">!</div>
            <div>
                <h3 style="color:#991b1b;">{html.escape(title)}</h3>
                <p style="color:#7f1d1d;">{html.escape(body)}</p>
            </div>
        </div>
    </div>
    """


def investigate(case_id: str) -> str:
    case_id = (case_id or "").strip().upper()

    if not case_id:
        return _error(
            "Case ID required",
            "Enter an investigation case ID or select one from the demo catalogue.",
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

        return _error(
            "Investigation failed",
            str(detail),
        )

    except requests.exceptions.RequestException:
        return _error(
            "Connection error",
            "Could not reach the investigation service. Verify that the API is running.",
        )

    findings = result.get("findings", [])
    confidence = result.get("confidence", "UNKNOWN").upper()
    status = result.get("status", "PENDING_REVIEW")
    conclusion = result.get("conclusion", "")
    recommendation = result.get("recommendation", "")

    complaint = CASE_CATALOGUE.get(
        case_id,
        "Investigation case submitted for analysis.",
    )

    confidence_class = _confidence_class(confidence)

    # ---------------------------------------------------------
    # Findings
    # ---------------------------------------------------------

    findings_html = ""

    for i, finding in enumerate(findings, 1):
        description = html.escape(
            finding.get("description", "No description provided.")
        )

        evidence = finding.get("evidence", [])

        evidence_html = "".join(
            f"<li>{html.escape(str(item))}</li>"
            for item in evidence
        )

        if not evidence_html:
            evidence_html = (
                '<li style="color:#94a3b8;">'
                "No supporting evidence provided."
                "</li>"
            )

        findings_html += f"""
        <div class="finding">
            <div class="finding-title">
                Finding {i} — {description}
            </div>

            <ul class="evidence">
                {evidence_html}
            </ul>
        </div>
        """

    if not findings_html:
        findings_html = (
            '<div class="empty">No findings were reported.</div>'
        )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return f"""
    <div class="result-wrapper">

        <!-- Result Header -->
        <div class="result-header">

            <div>
                <div class="result-case">
                    {html.escape(case_id)}
                </div>

                <p class="result-complaint">
                    {html.escape(complaint)}
                </p>
            </div>

            <div class="result-badges">

                <span class="result-badge status-badge">
                    {html.escape(status)}
                </span>

                <span class="result-badge {confidence_class}">
                    {html.escape(confidence)}
                </span>

            </div>

        </div>


        <!-- Metrics -->
        <div class="metrics">

            <div class="metric">
                <span class="metric-label">Status</span>
                <span class="metric-value">
                    {html.escape(status)}
                </span>
            </div>

            <div class="metric">
                <span class="metric-label">Confidence</span>
                <span class="metric-value">
                    {html.escape(confidence)}
                </span>
            </div>

            <div class="metric">
                <span class="metric-label">Findings</span>
                <span class="metric-value">
                    {len(findings)}
                </span>
            </div>

        </div>


        <!-- Findings -->
        <div class="result-section">

            <span class="section-label">
                Evidence-Based Findings
            </span>

            {findings_html}

        </div>


        <!-- Conclusion -->
        <div class="result-section">

            <span class="section-label">
                Conclusion
            </span>

            <div class="conclusion-box">
                <p class="conclusion-text">
                    {html.escape(conclusion)}
                </p>
            </div>

        </div>


        <!-- Recommendation -->
        <div class="result-section">

            <span class="section-label">
                Advisory Recommendation
            </span>

            <div class="recommendation-box">

                <p class="recommendation-text">
                    {html.escape(recommendation)}
                </p>

                <p class="advisory-note">
                    Advisory only — no financial action is executed automatically.
                </p>

            </div>

        </div>


        <!-- Human Review -->
        <div class="review-box">

            <div class="review-icon">
                🔎
            </div>

            <div>
                <h3>Human Review Required</h3>

                <p>
                    This investigation is awaiting review by an
                    authorized operations officer. No refund, reversal,
                    balance adjustment, or other consequential action
                    is executed automatically.
                </p>
            </div>

        </div>

    </div>
    """


def _set_case(selection: str) -> str:
    if not selection:
        return ""

    return selection.split(" — ", 1)[0]


CASE_CHOICES = [
    f"{case_id} — {description}"
    for case_id, description in CASE_CATALOGUE.items()
]


# =============================================================
# UI
# =============================================================

with gr.Blocks(
    title="Financial Transaction Investigation Agent",
    css=CSS,
) as demo:

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    gr.HTML(
        """
        <div class="app-header">

            <div class="header-eyebrow">
                Financial Operations
            </div>

            <h1>
                Financial Transaction Investigation Agent
            </h1>

            <p>
                Evidence-driven investigation for financial transaction
                complaints. The agent correlates customer, account,
                transaction, ledger, and balance evidence through
                controlled MCP capabilities.
            </p>

            <div class="system-badges">

                <span class="system-badge">
                    <span class="dot"></span>
                    MCP CONNECTED
                </span>

                <span class="system-badge">
                    <span class="dot"></span>
                    READ-ONLY
                </span>

                <span class="system-badge">
                    <span class="dot"></span>
                    HUMAN REVIEW
                </span>

            </div>

        </div>
        """
    )


    # ---------------------------------------------------------
    # Main area
    # ---------------------------------------------------------

    with gr.Row(
        equal_height=False,
        elem_classes="main-grid",
    ):

        # -----------------------------------------------------
        # Left: Investigation controls
        # -----------------------------------------------------

        with gr.Column(
            scale=1,
            elem_classes="panel",
        ):

            gr.HTML(
                """
                <h2 class="panel-title">
                    New Investigation
                </h2>

                <p class="panel-subtitle">
                    Submit a financial complaint for evidence-based
                    investigation.
                </p>
                """
            )

            gr.HTML(
                """
                <span class="input-label">
                    Investigation Case ID
                </span>
                """
            )

            case_input = gr.Textbox(
                label="",
                placeholder="e.g. CASE-001",
                elem_classes="case-input",
                show_label=False,
            )

            run_btn = gr.Button(
                "Run Investigation",
                variant="primary",
                size="lg",
                elem_classes="run-button",
            )

            gr.HTML(
                """
                <span class="selector-label">
                    Demo Case Catalogue
                </span>
                """
            )

            catalogue = gr.Dropdown(
                label="",
                choices=CASE_CHOICES,
                value=None,
                elem_classes="case-select",
                show_label=False,
            )

            # -------------------------------------------------
            # Workflow
            # -------------------------------------------------

            gr.HTML(
                """
                <div class="workflow">

                    <p class="workflow-title">
                        Investigation Pipeline
                    </p>

                    <div class="workflow-step">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <strong>Receive complaint</strong>
                            <span>Identify the investigation case</span>
                        </div>
                    </div>

                    <div class="workflow-step">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <strong>Collect evidence</strong>
                            <span>Retrieve evidence through MCP tools</span>
                        </div>
                    </div>

                    <div class="workflow-step">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <strong>Validate financial state</strong>
                            <span>Use deterministic financial logic</span>
                        </div>
                    </div>

                    <div class="workflow-step">
                        <div class="step-number">4</div>
                        <div class="step-content">
                            <strong>Correlate evidence</strong>
                            <span>Agent reasons over the collected evidence</span>
                        </div>
                    </div>

                    <div class="workflow-step">
                        <div class="step-number">5</div>
                        <div class="step-content">
                            <strong>Human review</strong>
                            <span>Recommendation only — no execution</span>
                        </div>
                    </div>

                </div>
                """
            )


        # -----------------------------------------------------
        # Right: Investigation result
        # -----------------------------------------------------

        with gr.Column(
            scale=2,
            elem_classes="panel ready-panel",
        ):

            result_output = gr.HTML(
                value="""
                <div class="ready-state">

                    <div class="ready-icon">
                        ⌕
                    </div>

                    <h2>
                        Ready for Investigation
                    </h2>

                    <p>
                        Enter a case ID or select a demo case from the
                        catalogue. The agent will collect evidence,
                        validate financial state, correlate the findings,
                        and return an advisory result.
                    </p>

                    <p class="ready-hint">
                        <strong>Safety boundary:</strong>
                        The agent can investigate and recommend.
                        It cannot execute consequential financial actions.
                    </p>

                </div>
                """
            )


    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    gr.HTML(
        """
        <div class="app-footer">
            Financial Transaction Investigation Agent
            &nbsp;·&nbsp;
            Controlled MCP capabilities
            &nbsp;·&nbsp;
            Deterministic financial validation
            &nbsp;·&nbsp;
            Human authorization required
        </div>
        """
    )


    # ---------------------------------------------------------
    # Events
    # ---------------------------------------------------------

    run_btn.click(
        fn=investigate,
        inputs=case_input,
        outputs=result_output,
        show_progress="full",
    )

    case_input.submit(
        fn=investigate,
        inputs=case_input,
        outputs=result_output,
        show_progress="full",
    )

    catalogue.change(
        fn=_set_case,
        inputs=catalogue,
        outputs=case_input,
    )


# =============================================================
# Launch
# =============================================================

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    theme=gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        neutral_hue=gr.themes.colors.slate,
        font=gr.themes.GoogleFont("Inter"),
    ),
)