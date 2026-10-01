# Evaluation Methodology

## Purpose

The evaluation is a deterministic regression suite for investigation
correctness and a comparison between the rule-based baseline and the LLM
investigation workflow. It is not a claim of production readiness.

## Dataset

The suite contains 20 synthetic cases covering successful, failed, reversed,
duplicate-looking, and multi-transaction investigations. Evidence is evaluated
as of each case's `submitted_at` timestamp. Transactions and ledger entries
created later are excluded.

Generate the evidence snapshot with:

```bash
uv run python -m evaluation.generate_ground_truth
```

The generated `evaluation/results/ground_truth.json` is hashed into every
result artifact.

## Scoring

Each case has deterministic required, alternative, and forbidden criteria.
The lexical matcher:

- is case-insensitive;
- normalizes numeric thousands separators;
- matches whole terms; and
- does not count directly negated claims.

A case is fully correct only when every criterion passes. Reports include both
fully correct cases and aggregate criteria passed. The current lexical rubric
is intentionally deterministic, but it does not replace domain-expert review
or a future typed fact contract.

## Reproducibility

Artifacts use schema version 2 and contain:

- rubric and ground-truth hashes;
- provider, model, prompt, and implementation identity;
- generation settings, including temperature;
- Python and git metadata;
- stored system output; and
- per-criterion reasons.

Existing agent results are resumed only when identity metadata matches. Gemini
`429` and `5xx` responses receive bounded retries. Strict comparison rejects
legacy artifacts, mismatched hashes, duplicate cases, and incomplete case sets.

## Commands

```bash
uv run python -m evaluation.baseline.run_evaluation
uv run python -m evaluation.agent.run_evaluation
uv run python -m evaluation.compare
```

Stored outputs can be rescored after a rubric-only change:

```bash
uv run python -m evaluation.rescore evaluation/results/agent.json
```

Ground-truth changes require explicit acknowledgement because outputs should
normally be regenerated when model inputs change.

## Current Results

| System | Fully correct cases | Criteria |
| --- | ---: | ---: |
| Deterministic baseline | 20 / 20 | 108 / 108 |
| Investigation agent | 17 / 20 | 103 / 108 |

The remaining agent failures are CASE-005, CASE-018, and CASE-019. They omit or
misattribute transaction evidence that was present in the supplied records.

## Limitations

- The dataset is small and reuses a limited set of synthetic transactions.
- One temperature-zero run does not measure model variance.
- Criteria still evaluate normalized text rather than typed financial facts.
- The criteria have not been independently signed off by a financial domain
  expert.
- Results should be reported with the model and artifact hashes, not as timeless
  model-performance claims.