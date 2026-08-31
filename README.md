# Financial Transaction Investigation Agent

> An agentic workflow for helping financial operations officers investigate customer transaction complaints by gathering and correlating evidence through controlled MCP capabilities, while keeping financial logic deterministic and final decisions under human authority.

## Overview

Financial transaction complaints often require evidence from multiple sources: customers, accounts, transactions, ledger entries, and account balances.

The challenge is not simply retrieving this information. An investigator must determine **which evidence is relevant, correlate it, identify inconsistencies, and decide what should be investigated next**.

This project explores whether an LLM-powered investigation agent can reduce that effort while maintaining:

* controlled access to financial capabilities;
* deterministic financial calculations;
* structured investigation results;
* auditable investigation trajectories; and
* mandatory human review for consequential decisions.

### Core principle

> **Intent guides the search → Evidence supports the finding → MCP defines the boundary → Human oversight owns the outcome.**

---

## How It Works

```text
Customer Complaint
        │
        ▼
Investigation Agent
        │
        │ interprets intent
        │ selects required evidence
        │ analyzes returned evidence
        │ determines next step
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
Synthetic Core-Banking Data
```

The agent does **not** access the database directly.

```text
Agent reasoning
      ↓
MCP capability
      ↓
Business service
      ↓
Financial data
```

This separates probabilistic reasoning from deterministic financial logic.

---

## Investigation Workflow

The investigation is evidence-driven rather than a fixed sequence.

```text
Complaint
   ↓
Interpret intent
   ↓
Determine required evidence
   ↓
Select MCP capability
   ↓
Gather evidence
   ↓
Analyze evidence
   ↓
More evidence required?
   ├── Yes → Select next step
   └── No
        ↓
     Finding
        ↓
  Recommendation
        ↓
 Human review
        ↓
 PENDING_REVIEW
```

The agent can determine:

* what the complaint is asking;
* which evidence is relevant;
* which permitted capability should be used;
* whether the evidence supports or contradicts the investigation;
* whether more evidence is required; and
* when there is sufficient evidence for a finding.

---

## Example

**Complaint**

> "I transferred 5,000 ETB yesterday, but my account balance is wrong."

The agent can investigate the relevant transactions, retrieve ledger evidence, and use the deterministic balance-comparison capability.

A resulting investigation may contain:

```text
Finding:
Potential duplicate debit of 5,000 ETB.

Evidence:
- Two matching transaction records were identified.
- Ledger evidence indicates inconsistent posting.
- Reported and expected balances differ.

Recommendation:
Escalate for reconciliation and verify the settlement status
of the suspected duplicate transaction.

Status:
PENDING_REVIEW
```

The recommendation is advisory. The system does not automatically refund, reverse, adjust, or otherwise modify a customer's financial state.

---

## Architecture

```text
┌──────────────────────────────┐
│      Operations Officer      │
│                              │
│ Review evidence              │
│ Make final decision          │
└──────────────▲───────────────┘
               │
               │ Finding + Evidence
               │ + Recommendation
               │
┌──────────────┴───────────────┐
│     Investigation Agent      │
│                              │
│ Intent → Evidence → Finding  │
└──────────────▲───────────────┘
               │
               │ Tool calls
               │
┌──────────────┴───────────────┐
│          MCP Client          │
└──────────────▲───────────────┘
               │
               │ MCP
               │
┌──────────────┴───────────────┐
│          MCP Server           │
│                               │
│ get_customer                  │
│ get_account                   │
│ get_transactions              │
│ get_ledger_entries            │
│ compare_account_balance       │
└──────────────▲────────────────┘
               │
┌──────────────┴───────────────┐
│     Synthetic Core Banking   │
│                              │
│ Customers                    │
│ Accounts                     │
│ Transactions                 │
│ Ledger Entries               │
└──────────────────────────────┘
```

### Component responsibilities

| Component               | Responsibility                                                                                 |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| **LLM**                 | Interpret complaints, select evidence, correlate information, and generate structured findings |
| **Investigation Agent** | Coordinate the investigation workflow                                                          |
| **MCP**                 | Define and enforce the permitted tool boundary                                                 |
| **Business Services**   | Perform deterministic financial and business logic                                             |
| **Pydantic**            | Constrain agent actions and investigation results                                              |
| **Operations Officer**  | Make the final consequential decision                                                          |

### Financial authority

The LLM is **not** responsible for:

* financial calculations;
* balance reconciliation;
* transaction posting;
* refunds;
* reversals;
* account modifications; or
* final consequential decisions.

---

## MCP Capabilities

The investigation agent currently uses read-only capabilities:

| Tool                      | Purpose                                  |
| ------------------------- | ---------------------------------------- |
| `get_customer`            | Retrieve customer information            |
| `get_account`             | Retrieve account information             |
| `get_transactions`        | Retrieve transaction records             |
| `get_ledger_entries`      | Retrieve ledger evidence                 |
| `compare_account_balance` | Perform deterministic balance comparison |

The agent cannot bypass the MCP boundary to access the underlying database.

---

## Structured Interfaces

Agent actions and investigation results use structured Pydantic schemas.

```text
InvestigationAction
├── intent
├── reason
├── tool
├── parameters
└── expected_evidence
```

```text
InvestigationResult
├── case_summary
├── investigation_intent
├── findings
├── evidence
├── anomalies
├── confidence
├── recommendation
└── requires_human_review
```

This provides a predictable contract between the LLM, agent, MCP layer, and application.

---

## Human Review

Human review is a required boundary of the system.

```text
Investigation
      ↓
Finding + Evidence
      ↓
Recommendation
      ↓
Human Checkpoint
      ↓
PENDING_REVIEW
      ↓
Qualified Operations Officer
      ↓
Final Decision
```

The agent cannot approve, reject, refund, reverse, or otherwise execute a consequential financial action.

The final decision belongs to the qualified operations officer.

---

## Investigation Trajectories

Each investigation can produce a trajectory describing the workflow execution.

Trajectories provide an auditable record of:

* investigation steps;
* MCP tool interactions;
* evidence gathered;
* retries when they actually occur;
* human checkpoints; and
* final investigation state.

MCP retries are recorded only when a genuine retry occurs.

Trajectory recording is covered by automated tests for successful investigations, genuine retries, multiple retries, ordering, and retry timestamps.

---

## Evaluation

The project evaluates the agent against a deterministic baseline using the same synthetic dataset and **20 investigation cases**.

The cases cover normal transactions, failed and reversed transactions, incoming and outgoing transfers, duplicate-looking transfers, and inconsistent account/ledger states.

### Current results

| System              |     Correct | Accuracy |
| ------------------- | ----------: | -------: |
| Simple baseline     | **20 / 20** | **100%** |
| Investigation agent | **19 / 20** |  **95%** |

The baseline therefore remains more accurate on the current deterministic evaluation.

This is an intentional part of the experiment: adding an LLM does not automatically improve correctness.

The goal is to evaluate whether an agent provides value through **adaptive investigation, evidence correlation, and reduced manual effort**, while deterministic services remain authoritative for financial logic.

Detailed case-level ground truth and evaluation outputs are maintained under:

```text
evaluation/results/
```

---

## Key Insight

> **Use agents where adaptation and evidence correlation matter; use deterministic software where correctness can be explicitly defined.**

Financial calculations and reconciliation should remain deterministic and verifiable.

The agent is most useful as an **investigation coordinator and reasoning layer** that can interpret an unstructured complaint, determine what evidence is needed, select permitted capabilities, and correlate evidence across financial sources.

---

## Project Structure

```text
app/
├── agent/          # Investigation agent, schemas and trajectories
├── api/            # API endpoints
├── data/           # Database and synthetic data
├── llm/            # LLM provider abstraction
├── mcp/            # MCP client, server and tools
├── models/         # Domain models
└── services/       # Deterministic business logic

evaluation/
├── agent/          # Agent evaluation
├── baseline/       # Baseline evaluation
├── cases/          # Evaluation cases
├── results/        # Evaluation outputs and trajectories
└── compare.py      # Baseline/agent comparison

tests/
├── unit/
├── integration/
└── evaluation/
```

---

## Quick Start

### 1. Configure the LLM

```bash
cp .env.example .env
```

Configure the required provider credentials in `.env`.

Example:

```env
DEFAULT_LLM_PROVIDER=your_llm_provider
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=your_model
```

### 2. Start the application

```bash
docker compose up --build
```

### 3. Run an investigation

Submit a transaction complaint through the available API/UI.

The system will:

```text
Complaint
   ↓
Agent
   ↓
MCP evidence gathering
   ↓
Evidence correlation
   ↓
Finding
   ↓
Recommendation
   ↓
Human review
```

### 4. Run tests

```bash
uv run pytest tests/unit -v
```

Current unit-test status:

```text
46 passed
```

### 5. Run the evaluation

The evaluation runners are available under:

```text
evaluation/
```

The baseline and agent are evaluated against the same cases.

---

## Technology

* Python
* FastAPI
* Pydantic
* SQLite
* Model Context Protocol (MCP)
* LLM provider abstraction
* Docker / Docker Compose
* Pytest
* uv

The project intentionally uses:

> **One investigation agent + controlled MCP capabilities + deterministic business logic + structured results + mandatory human review.**

It does not depend on LangGraph or multi-agent orchestration.

---

## Project Status

🚧 **Active Development**

### Implemented

* Investigation domain and data models
* Deterministic service layer
* MCP server and client
* Read-only financial investigation tools
* Investigation agent
* Structured agent interfaces
* Synthetic evaluation dataset
* Deterministic baseline
* Agent evaluation
* Investigation trajectories
* MCP retry recording
* Automated tests

### Current evidence

```text
Unit tests:        46 / 46 passing
Baseline:          20 / 20 (100%)
Agent:             19 / 20 (95%)
```

### Next Priority

The immediate priority is to **integrate the investigation agent with the application frontend/API and demonstrate the complete user-facing workflow**.

After that, remaining time should be used to:

1. investigate the current agent failure;
2. make targeted improvements where justified;
3. rerun the evaluation;
4. finalize evaluation artifacts; and
5. prepare the final hackathon demo.

---

## Safety Boundary

This project is an **investigation assistant**, not an autonomous financial decision-maker.

```text
INVESTIGATE
     ↓
CORRELATE EVIDENCE
     ↓
EXPLAIN FINDINGS
     ↓
RECOMMEND
     ↓
REQUEST HUMAN REVIEW
```

The system does not autonomously make or execute consequential financial decisions.

The final authority remains with the qualified human operations officer.
