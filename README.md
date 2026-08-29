# Financial Transaction Investigation Agent

> An agentic workflow that helps banking and financial operations officers investigate customer transaction complaints by reasoning over evidence from core banking systems through controlled MCP tools and producing an evidence-based investigation report and recommendation for human review.

## Problem

Financial operations officers investigate customer complaints such as:

> "I transferred 5,000 ETB, but my account balance is incorrect."

The information required to investigate is distributed across multiple core banking data sources, including customer records, account information, transaction history, ledger entries, and account balances.

An officer must manually identify the relevant records, correlate information across these sources, determine whether the records are consistent, and establish what actually happened.

The bottleneck is therefore not simply **data retrieval**. It is **correlating evidence and determining what should be investigated next**.

---

## Core Approach

The system is designed around four principles:

> **Intent guides the search → Evidence proves the claim → MCP defines the boundaries → Human oversight owns the outcome.**

The agent does not directly access the core banking database and does not make consequential financial decisions.

Instead:

* The **LLM** interprets the complaint, determines investigation intent, selects appropriate tools, analyzes evidence, and decides what information is still required.
* **MCP** provides controlled access to permitted investigation capabilities.
* **Business services** perform deterministic financial and business calculations.
* **Pydantic** provides structured boundaries for API inputs, agent actions, and investigation results.
* The **operations officer** reviews the investigation result and remains responsible for the final decision and any consequential action.

The architecture intentionally uses **one investigation agent** rather than multiple specialized agents or LangGraph. The flexibility comes from evidence-driven investigation rather than unnecessary orchestration complexity.

---

## Example Investigation

### Customer Complaint

> "I transferred 5,000 ETB yesterday, but my account balance is wrong."

### Investigation

The agent may determine that the complaint requires transaction and balance investigation.

It could then:

```text
Complaint
   ↓
Understand intent
   ↓
Retrieve relevant transactions
   ↓
Analyze transaction evidence
   ↓
Identify possible anomaly
   ↓
Retrieve additional ledger evidence
   ↓
Compare account and ledger balances
   ↓
Determine whether the evidence supports the finding
   ↓
Produce investigation report
```

The important point is that this is **not a fixed sequence**.

The next investigation step depends on the evidence returned by the previous step.

For example, if transaction data suggests a possible duplicate, the agent may request ledger evidence to determine whether both transactions were actually posted. If the ledger and account balance disagree, it may then request a deterministic balance comparison.

### Example Result

```text
Finding:
A potential duplicate debit of 5,000 ETB was identified.

Evidence:
- Two transactions have the same sender, recipient, amount and date.
- Only one corresponding recipient credit exists.
- The ledger and reported account balance are inconsistent.
- The balance difference equals 5,000 ETB.

Recommendation:
Escalate for reconciliation and verify the settlement status
of the suspected duplicate transaction.

Human decision required:
Yes
```

The recommendation is advisory. The system does not automatically perform a refund, reversal, balance adjustment, or other consequential action.

---

## Architecture

```text
                    ┌──────────────────────────┐
                    │    Operations Officer    │
                    │                          │
                    │ Review result            │
                    │ Make final decision      │
                    └────────────▲─────────────┘
                                 │
                                 │ Investigation Report
                                 │ + Evidence
                                 │ + Recommendation
                                 │
                    ┌────────────┴─────────────┐
                    │   Investigation Agent    │
                    │                          │
                    │ Intent → Evidence →      │
                    │ Next Investigation Step  │
                    └────────────▲─────────────┘
                                 │
                                 │ Tool Calls
                                 │
                    ┌────────────┴─────────────┐
                    │       MCP Client         │
                    └────────────▲─────────────┘
                                 │
                                 │ MCP
                                 │
                    ┌────────────┴─────────────┐
                    │       MCP Server         │
                    │                          │
                    │ get_customer             │
                    │ get_account              │
                    │ get_transactions         │
                    │ get_ledger_entries       │
                    │ compare_account_balance  │
                    └────────────▲─────────────┘
                                 │
                                 │
                    ┌────────────┴─────────────┐
                    │   Core Banking Data      │
                    │                          │
                    │ Customers                │
                    │ Accounts                 │
                    │ Transactions             │
                    │ Ledger Entries           │
                    └──────────────────────────┘
```

### Investigation Flow

```text
Customer Complaint
        ↓
Investigation Agent
        ↓
Interpret Intent
        ↓
Select Evidence Required
        ↓
MCP Tool
        ↓
Structured Tool Result
        ↓
Analyze Evidence
        ↓
Is more evidence required?
       / \
     Yes  No
      │    │
      │    └──────────────┐
      ↓                   ↓
Next Investigation      Final Finding
Step                       ↓
      │                 Recommendation
      │                       ↓
      └──────→ Agent         ↓
                          Operations
                            Officer
```

---

## Agentic Investigation Model

The agent maintains investigation context throughout the execution.

Conceptually:

```text
Complaint
   ↓
Investigation Intent
   ↓
Evidence Collected
   ↓
Current Findings / Hypotheses
   ↓
Unresolved Questions
   ↓
Next Investigation Action
   ↓
Additional Evidence
   ↓
Final Finding
```

After each MCP call, the returned evidence becomes part of the investigation context.

The agent evaluates:

* What does this evidence establish?
* Does it support or contradict the current hypothesis?
* What remains unknown?
* Is additional evidence required?
* Which permitted capability can provide that evidence?
* Is there enough evidence to produce a defensible finding?

This allows the agent to adapt its investigation path to the complaint and the evidence discovered during execution.

---

## Controlled MCP Capabilities

The initial MCP capabilities are intentionally limited to read-only investigation operations:

| Tool                      | Purpose                                  |
| ------------------------- | ---------------------------------------- |
| `get_customer`            | Retrieve customer information            |
| `get_account`             | Retrieve account information             |
| `get_transactions`        | Retrieve relevant transaction records    |
| `get_ledger_entries`      | Retrieve ledger evidence                 |
| `compare_account_balance` | Perform deterministic balance comparison |

The agent cannot bypass these interfaces to access the underlying database directly.

This creates a clear separation:

```text
Agent reasoning
      ↓
MCP capability
      ↓
Business service
      ↓
Core banking data
```

MCP therefore acts as the **capability and access boundary** between agent reasoning and financial data.

---

## LLM and Deterministic Logic

The LLM is used where interpretation and reasoning are required:

* understanding the complaint;
* identifying investigation intent;
* selecting appropriate tools;
* interpreting tool results;
* correlating evidence;
* identifying inconsistencies;
* determining whether additional evidence is required;
* forming an evidence-based finding; and
* generating a recommendation.

Financial calculations and business rules remain deterministic.

For example:

```text
Agent:
"Check whether the account balance is consistent."

        ↓

MCP
        ↓

compare_account_balance()

        ↓

Deterministic Result

expected_balance = 20,000
reported_balance = 15,000
difference = 5,000
consistent = false

        ↓

Agent interprets the evidence
```

The LLM therefore does not become the authority for financial calculations.

---

## Structured Agent Decisions

Pydantic schemas constrain the LLM-facing interfaces.

Agent decisions are represented as structured data containing information such as:

```text
InvestigationAction
├── intent
├── reason
├── tool
├── parameters
└── expected_evidence
```

The final investigation result is also structured:

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

This reduces reliance on free-form LLM output and provides predictable interfaces between the agent, MCP layer, and API.

---

## Human Oversight

The system is an **investigation assistant**, not an autonomous financial decision-maker.

The agent produces:

```text
Finding
   +
Evidence
   +
Confidence
   +
Recommendation
```

The operations officer reviews the result and decides what action, if any, should be taken.

The system does not automatically perform:

* refunds;
* transaction reversals;
* balance adjustments;
* account changes; or
* other consequential financial actions.

---

## Evaluation

The project will be evaluated against a simple baseline using the **same investigation cases and underlying synthetic data**.

The evaluation will contain 10+ cases covering scenarios such as:

* normal transactions;
* duplicate transactions;
* missing recipient credits;
* balance discrepancies;
* missing ledger entries;
* reversed transactions;
* unexpected fees;
* ledger duplication; and
* multiple simultaneous anomalies.

### Primary Metric

**Investigation Accuracy**

> Whether the system reaches the expected investigation finding for a given case.

Supporting measurements include:

| Metric                   | What it measures                                             |
| ------------------------ | ------------------------------------------------------------ |
| Investigation Accuracy   | Whether the expected issue is correctly identified           |
| Evidence Accuracy        | Whether relevant supporting evidence is correctly identified |
| Unsupported Claims       | Whether conclusions are made without supporting evidence     |
| Human Investigation Time | Reduction in manual investigation effort                     |
| Cost per Investigation   | Approximate execution cost                                   |

The same cases and evaluation criteria will be used for both the baseline and the agent.

---

## Improvement Changelog

The project will document the evolution of the workflow through measurable experiments.

| Stage       | Experiment                             | Evidence          | Decision                   |
| ----------- | -------------------------------------- | ----------------- | -------------------------- |
| Baseline    | Simple investigation approach          | Evaluation result | Establish starting point   |
| Iteration 1 | Introduce MCP investigation tools      | Evaluation result | Keep / revise / remove     |
| Iteration 2 | Introduce intent-driven tool selection | Evaluation result | Keep / revise / remove     |
| Iteration 3 | Introduce structured agent decisions   | Evaluation result | Keep / revise / remove     |
| Iteration 4 | Introduce evidence-driven next steps   | Evaluation result | Keep / revise / remove     |
| Final       | Combine successful changes             | Final evaluation  | Identify main contribution |

Actual measurements will be added as experiments are completed.

Experiments that fail to improve the workflow will also be documented.

---

## Reproducibility

The project uses synthetic financial data so that the complete workflow can be reproduced without exposing private customer information.

A clean environment will be able to:

1. Start the application.
2. Initialize the SQLite database.
3. Load the synthetic core banking data.
4. Start the MCP server.
5. Submit a customer complaint.
6. Run the investigation agent.
7. Observe the investigation trajectory.
8. Inspect the final investigation report.
9. Run the baseline.
10. Run the evaluation cases.
11. Compare the results.

The repository will provide the required setup commands, configuration, versions, expected outputs, evaluation procedure, and approximate runtime and cost.

---

## Technology

* **Python**
* **FastAPI**
* **Pydantic**
* **SQLite** — synthetic core banking dataset
* **Model Context Protocol (MCP)** — controlled tool access
* **LLM provider abstraction** — OpenAI, Anthropic, Gemini, or compatible providers
* **Docker / Docker Compose**
* **Chat UI**
* **Pytest** — testing and evaluation

The architecture intentionally avoids LangGraph and multi-agent orchestration.

The core design is:

> **One investigation agent + controlled MCP capabilities + deterministic business logic + structured LLM decisions + human review.**

---

## Status

🚧 **Active Development**

The project is being implemented incrementally.

The README will be updated with actual evaluation results, investigation trajectories, improvement experiments, known failure modes, and final findings as the implementation progresses.
