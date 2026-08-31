# Financial Transaction Investigation Agent

> **An agentic workflow that helps financial operations officers investigate customer transaction complaints by gathering and correlating evidence through controlled MCP capabilities—while keeping financial logic deterministic and final decisions under human authority.**

---

## Why This Problem?

Financial operations teams regularly handle customer complaints such as:

* “I was charged twice.”
* “My transfer failed, but my balance decreased.”
* “The recipient received the money, but my account still looks wrong.”
* “A reversed transaction did not restore my balance.”

Investigating these complaints is rarely a matter of checking a single record.

The relevant evidence may be distributed across:

* customer records;
* account information;
* transaction history;
* ledger entries; and
* calculated account balances.

An operations officer must identify which evidence matters, correlate records across these sources, detect inconsistencies, and determine what should be reviewed next.

The bottleneck is therefore **evidence correlation and investigation effort**, not simply data retrieval.

This project explores whether an agent can make financial investigations more systematic and reduce the effort required to correlate evidence, while keeping financial correctness and consequential decisions outside the LLM.

---

# The Solution

The **Financial Transaction Investigation Agent** acts as an investigation coordinator.

It interprets the complaint, determines what evidence is relevant, uses controlled MCP capabilities to retrieve that evidence, correlates the results, and produces a structured investigation report.

The architecture deliberately separates **probabilistic reasoning** from **deterministic financial logic**.

```text
Customer Complaint
        │
        ▼
Investigation Agent
        │
        │ Interpret investigation objective
        │ Determine relevant evidence
        │ Select permitted capabilities
        │ Correlate evidence
        ▼
    MCP Client
        │
        ▼
    MCP Server
        │
        ├── get_customer
        ├── get_account
        ├── get_transactions
        ├── get_ledger_entries
        └── compare_account_balance
        │
        ▼
Deterministic Business Services
        │
        ▼
Synthetic Financial Data
```

The agent **never accesses the database directly**.

```text
Agent reasoning
      ↓
MCP capability
      ↓
Business service
      ↓
Financial data
```

This creates a clear boundary between what the agent can reason about and what the financial system is allowed to determine.

---

# What Makes It Agentic?

The investigation is designed around an agent that works with an investigation objective and available evidence rather than generating a fixed financial decision.

```text
Complaint
    ↓
Interpret investigation objective
    ↓
Determine relevant evidence
    ↓
Select permitted MCP capability
    ↓
Gather evidence
    ↓
Correlate and analyze evidence
    ↓
Generate findings
    ↓
Generate recommendation
    ↓
Human checkpoint
```

The agent can:

* interpret an unstructured complaint;
* identify relevant evidence;
* select permitted MCP capabilities;
* correlate customer, account, transaction, and ledger information;
* identify inconsistencies and potential anomalies; and
* produce evidence-backed findings and recommendations.

The project intentionally uses **one investigation agent** rather than adding multiple agents or orchestration frameworks simply for complexity.

The goal is to demonstrate useful agentic behavior while keeping the system understandable, auditable, and safe.

---

# Example Investigation

## Customer Complaint

> “I transferred 5,000 ETB yesterday, but my account balance is wrong.”

The agent investigates the relevant account and retrieves transaction, ledger, and balance evidence.

### Example Finding

```text
Finding:

Potential duplicate debit of 5,000 ETB.

Evidence:

- TX-1001 and TX-1004 are both successful 5,000 ETB transfers.
- Both transfers were made to ACC-1002.
- The transactions occurred within two minutes.
- Separate debit ledger entries exist for both transactions.
- The deterministic balance comparison reports a discrepancy.

Recommendation:

Perform manual reconciliation and verify whether both
transfers were authorized by the customer.
```

The agent does **not** decide whether a refund or reversal should occur.

The resulting case status is:

```text
PENDING_REVIEW
```

The case is then passed to an authorized operations officer.

---

# Financial Safety Boundary

This is an **investigation assistant**, not an autonomous financial decision-maker.

The LLM is not responsible for:

* calculating balances;
* determining authoritative financial state;
* posting transactions;
* issuing refunds;
* performing reversals;
* modifying accounts; or
* making the final consequential decision.

Financial calculations and business rules remain deterministic.

The agent can recommend an action, but **a qualified human must make the final decision**.

```text
INVESTIGATE
     ↓
CORRELATE EVIDENCE
     ↓
EXPLAIN FINDINGS
     ↓
RECOMMEND
     ↓
HUMAN REVIEW
     ↓
FINAL DECISION
```

No consequential financial action is automatically executed by the system.

---

# MCP Capabilities

The agent operates through read-only MCP capabilities:

| MCP Tool                  | Purpose                                  |
| ------------------------- | ---------------------------------------- |
| `get_customer`            | Retrieve customer information            |
| `get_account`             | Retrieve account information             |
| `get_transactions`        | Retrieve account transactions            |
| `get_ledger_entries`      | Retrieve ledger evidence                 |
| `compare_account_balance` | Perform deterministic balance comparison |

MCP provides the controlled capability boundary between the agent and financial services.

The MCP layer does not expose financial write operations.

---

# Structured Results

Agent results use structured Pydantic models rather than unconstrained text.

## Investigation Result

```text
InvestigationResult

├── case_id
├── findings
│   ├── description
│   └── evidence
├── conclusion
├── confidence
│   └── HIGH | MEDIUM | LOW
├── recommendation
├── requires_human_review
└── status
    └── PENDING_REVIEW
```

The application enforces:

```text
requires_human_review = True
status = PENDING_REVIEW
```

in application code, independently of the LLM response.

This prevents the model from bypassing the human-review boundary through its generated output.

---

# Investigation Trajectories

Every evaluation investigation produces a trajectory that records how the investigation was executed.

A trajectory captures:

* workflow start, including the investigation objective and instructions;
* case retrieval;
* each MCP tool call, including parameters and return values;
* the investigation prompt assembled from evidence;
* LLM request and response confirmation;
* result validation;
* the mandatory `human_checkpoint` event; and
* the final validated investigation result.

MCP retry events are recorded **only when an actual retry occurs**. They are not artificially inserted into successful trajectories.

All 20 evaluation trajectories are stored under:

```text
evaluation/results/trajectories/
```

Each file is named:

```text
CASE-NNN.json
```

and contains the recorded investigation steps from workflow start through the human checkpoint and final validated result.

Customer PII is sanitized before trajectories are persisted.

Investigation identifiers such as `customer_id`, `account_id`, and `transaction_id` are preserved for traceability.

---

# Evaluation

The project uses a deterministic baseline and evaluates both systems against the **same 20 synthetic investigation cases**.

The evaluation set includes:

* normal incoming and outgoing transactions;
* failed transactions;
* reversed transactions;
* duplicate-looking transactions;
* multi-transaction investigations; and
* inconsistent account and ledger states.

The evaluation measures whether the agent reaches the expected investigation outcome against the same deterministic reference used by the baseline.

The goal is not simply to produce plausible investigation narratives.

> **The evaluation measures whether the agent reaches the expected investigation outcome, not simply whether it produces a plausible narrative.**

## Evaluation Results

| System                 |     Correct | Accuracy |
| ---------------------- | ----------: | -------: |
| Deterministic baseline | **20 / 20** | **100%** |
| Investigation agent    | **15 / 20** |  **75%** |

The criteria-level result is:

**93 / 98 (95%)**

across all 20 cases.

## Agent Failure Cases

| Case     | Score | Failing Criterion                 |
| -------- | ----: | --------------------------------- |
| CASE-003 |   80% | Identifies 1,000 ETB reversal     |
| CASE-005 |   75% | Identifies TX-1002                |
| CASE-006 |   75% | Identifies successful transaction |
| CASE-008 |   75% | Identifies successful transaction |
| CASE-009 |   80% | Identifies suspected duplicate    |

The deterministic baseline currently outperforms the agent on correctness.

That result is important.

The project does **not** claim that adding an LLM automatically improves financial investigation accuracy.

Instead, the experiment evaluates where an agent can provide value beyond deterministic rules:

* interpreting complaints;
* adapting evidence collection;
* correlating information;
* explaining relationships between records; and
* reducing investigation effort.

Detailed evaluation cases and results are available under:

```text
evaluation/
```

---

# Hot Take / Insights

> **An agent should not be trusted simply because it can reason across more evidence. In financial workflows, adaptive reasoning is valuable, but every reasoning step can also introduce error.**

The evaluation demonstrated this directly:

```text
Deterministic baseline: 20/20  (100%)
Investigation agent:    15/20   (75%)
```

The **15/20 versus 20/20** result is part of the project's evidence—not something to hide.

It demonstrates where probabilistic reasoning can help and where deterministic authority is still required.

## Where the Agent Adds Value

The agent is useful when the task requires:

* interpreting ambiguous or unstructured complaints;
* deciding which evidence is relevant;
* navigating permitted capabilities;
* correlating evidence across multiple sources;
* explaining relationships between records; and
* producing an investigation narrative for a human reviewer.

## Where Deterministic Software Should Remain Authoritative

When correctness can be explicitly defined and tested, deterministic software should own the decision.

That includes:

* financial calculations;
* balance comparison;
* reconciliation rules;
* transaction and ledger logic; and
* financial state changes.

## Main Failure Mode

The agent can produce an incorrect investigation result even when the underlying evidence is available.

The five failing cases — **CASE-003, CASE-005, CASE-006, CASE-008, and CASE-009** — involved evidence that was present in the tool responses but was not correctly identified or attributed in the LLM output.

The response to an agent failure should **not** be to give the agent more financial authority.

Instead, the system limits the consequences of probabilistic reasoning through:

1. controlled MCP capabilities;
2. deterministic financial services;
3. structured output validation;
4. evidence-backed findings;
5. trajectory recording;
6. mandatory human review; and
7. no autonomous consequential actions.

## The Lesson

> **Use agents where adaptation and evidence correlation matter. Use deterministic software where correctness can be explicitly defined. Keep consequential authority with qualified humans.**

---

# Improvement Changelog

The project was developed incrementally rather than starting with the final architecture.

| Stage           | What Changed                                                                                                      | Evidence / Learning                                                         | Decision                                                                  |
| --------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Baseline**    | Built a deterministic investigation baseline using the same synthetic cases                                       | **20/20 — 100%**                                                            | Established a strong correctness reference                                |
| **Iteration 1** | Introduced an LLM-based investigation workflow                                                                    | Agent could interpret investigation context and produce structured analysis | Kept the agent for reasoning and coordination                             |
| **Iteration 2** | Added controlled MCP capabilities for customer, account, transaction, and ledger evidence                         | Separated agent reasoning from direct database access                       | Kept                                                                      |
| **Iteration 3** | Added deterministic balance comparison                                                                            | Financial calculations no longer depended on LLM reasoning                  | Kept                                                                      |
| **Iteration 4** | Added structured Pydantic investigation results                                                                   | Reduced unconstrained agent output                                          | Kept                                                                      |
| **Iteration 5** | Added mandatory human checkpoint enforcement                                                                      | Prevented the agent from becoming an autonomous financial decision-maker    | Kept                                                                      |
| **Iteration 6** | Added trajectory recording and genuine MCP retry tracking                                                         | Made agent behavior and failures auditable                                  | Kept                                                                      |
| **Final**       | Combined controlled MCP access, deterministic financial logic, structured results, trajectories, and human review | **15/20 — 75%** agent accuracy                                              | Keep the agent as an investigation coordinator, not a financial authority |

### Removed Experiment

The project deliberately avoids unnecessary multi-agent orchestration.

Where multi-agent orchestration was considered as an architectural direction, the final design retained a single investigation agent because additional orchestration was not necessary to demonstrate the core problem or improve the investigation objective.

The final architecture therefore focuses on:

> **One investigation agent + controlled MCP capabilities + deterministic business logic + structured results + mandatory human review.**

The most important architectural improvement was not adding more agents.

It was **separating adaptive reasoning from authoritative financial logic**.

---

# Reproducibility

The project uses synthetic financial data so the evaluation can be reproduced without exposing customer information.

A new evaluator should be able to:

1. start the application;
2. run the deterministic baseline;
3. run the investigation agent;
4. evaluate the same 20 cases;
5. inspect the results; and
6. inspect the corresponding trajectories.

---

# Requirements

* Python 3.11+
* Docker / Docker Compose
* `uv`
* A Gemini API key

---

# Setup

Clone the repository:

```bash
git clone <repository-url>

cd financial-transaction-investigation-agent
```

Create the environment file:

```bash
cp .env.example .env
```

Configure the required values:

```env
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Start the application:

```bash
docker compose up --build
```

---

# Running Tests

Run the complete test suite:

```bash
uv run pytest tests/ -v
```

Test suite result:

```text
53 passed
```

---

# Running the Evaluation

Run the deterministic baseline:

```bash
uv run python -m evaluation.baseline.run_evaluation
```

Run the investigation agent evaluation:

```bash
uv run python -m evaluation.agent.run_evaluation
```

Compare baseline and agent results:

```bash
uv run python evaluation/compare.py
```

---

# User-Facing Demo

The project includes an operations investigation console built with **Gradio**.

The evaluator can enter a case ID such as:

```text
CASE-001
```

or select an evaluation case from the catalogue.

The interface displays:

* investigation status;
* confidence;
* complaint context;
* evidence-based findings;
* conclusion;
* advisory recommendation; and
* human-review requirement.

The UI is designed as an **operations investigation console**, not a generic chatbot.

The purpose is to show how an operations officer could use the system as an investigation assistant while retaining decision-making authority.

---

# Project Structure

```text
financial-transaction-investigation-agent/

├── app/
│   ├── agent/              # Investigation agent, schemas, trajectory
│   ├── api/                # API routes and schemas
│   ├── data/               # Database and synthetic data
│   ├── llm/                # LLM provider abstraction
│   ├── mcp/                # MCP client, server, and tools
│   ├── models/             # Domain models
│   └── services/           # Deterministic business logic
│
├── evaluation/
│   ├── agent/              # Agent evaluation runner
│   ├── baseline/           # Deterministic baseline runner
│   ├── cases/              # 20 evaluation cases
│   ├── results/
│   │   ├── agent.json      # Agent evaluation results
│   │   ├── baseline.json   # Baseline evaluation results
│   │   └── trajectories/   # Investigation trajectories
│   └── compare.py          # Baseline / agent comparison
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── frontend/               # Operations investigation console
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

# Technology

* **Python 3.11**
* **FastAPI**
* **Pydantic**
* **SQLite**
* **Model Context Protocol (MCP)**
* **Gemini / `google-genai`**
* **Docker / Docker Compose**
* **Pytest**
* **uv**
* **Gradio**

The project intentionally uses:

> **One investigation agent + controlled MCP capabilities + deterministic business logic + structured results + mandatory human review.**

It does not use LangGraph or multi-agent orchestration because additional orchestration was not necessary for the problem being solved.

---

# Project Status

## Implemented

* Financial investigation domain models
* Synthetic financial dataset
* Deterministic business services
* Deterministic evaluation baseline
* MCP server and client with retry handling
* Read-only financial investigation capabilities
* Investigation agent
* Structured agent result schema
* Deterministic balance comparison
* Human-review enforcement
* Investigation trajectories with PII sanitization
* Genuine MCP retry recording
* Automated tests
* 20-case evaluation
* Operations investigation UI

## Submission Evidence

```text
Unit + integration tests:   53 passing

Baseline:                   20 / 20  (100%)

Investigation agent:        15 / 20   (75%)

Criteria:                   93 / 98   (95%)
```

---

# Safety & Data

The evaluation uses **synthetic financial data**.

No production customer credentials or private customer information are required.

The system is intentionally read-only at the MCP capability level.

Customer PII such as:

* name;
* phone;
* email; and
* address

is stripped from investigation trajectories before they are saved.

Investigation identifiers such as:

* `customer_id`;
* `account_id`; and
* `transaction_id`

are preserved for traceability.

The system does not expose autonomous financial write operations.

> **The agent investigates and recommends. It does not execute consequential financial actions.**

---

# Final Principle

The central principle of this project is:

> **Use agents where adaptation and evidence correlation matter. Use deterministic software where correctness can be explicitly defined. Keep consequential authority with qualified humans.**

The project does not attempt to prove that an LLM is better than deterministic software at financial correctness.

Instead, it demonstrates a safer architecture for combining the two:

```text
                    ┌─────────────────────┐
                    │   Customer Complaint│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Investigation Agent │
                    │                     │
                    │ Reason + Correlate  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Controlled MCP    │
                    │    Capabilities     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Deterministic       │
                    │ Financial Services  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Evidence + Findings │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Human Review      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Final Decision    │
                    └─────────────────────┘
```

**The agent investigates. Deterministic software establishes financial truth. A qualified human retains consequential authority.**
