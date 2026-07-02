# runx Harness Guide

A practical walkthrough of the runx harness testing system — SKILL.md contracts, X.yaml test cases, fixtures, sealed receipts, and the publish-verify loop.

## What is runx?

[runx](https://runx.ai) is an open-source runtime for policy-bounded agent skills. Skills are packaged as a three-file unit:

- **SKILL.md** — the skill contract: what inputs it reads, what outputs it seals, and how it behaves
- **X.yaml** — the harness: inline test cases the hosted gate runs to prove the skill works
- **runner** — the implementation (shell, Python, JS, or MCP)

Every runx run seals a receipt that anyone can verify independently. That receipt is the unit of trust on the [Frantic](https://gofrantic.com) board and in the runx ecosystem.

## The Harness Loop

```
SKILL.md  +  X.yaml  +  fixtures/  →  runx harness  →  sealed receipt
                                                         ↓
                                              runx verify --receipt
```

### 1. SKILL.md — The Contract

Every skill starts with frontmatter that declares its identity, inputs, and outputs:

```yaml
---
name: example-validator
version: 0.1.0
description: Validates that input meets a policy threshold
inputs:
  score:
    type: integer
    description: The score to validate
    required: true
  threshold:
    type: integer
    description: Minimum passing score
    required: true
    default: 70
outputs:
  verdict:
    type: object
    description: Decision with pass/fail and reason
    properties:
      passed:
        type: boolean
      reason:
        type: string
run:
  kind: python
  file: run.py
---
```

The frontmatter is machine-readable. The `run` field tells runx how to execute the skill.

### 2. X.yaml — The Harness

Test cases live in `X.yaml`. Each case is a named scenario with a verdict expectation:

```yaml
cases:
  - name: passes_above_threshold
    verdict: SEALED
    input:
      score: 85
      threshold: 70
    expected:
      passed: true
      reason: Score 85 meets or exceeds threshold 70

  - name: fails_below_threshold
    verdict: STOP
    input:
      score: 50
      threshold: 70
```

- `SEALED` — the run must complete and seal a receipt
- `STOP` — the run must stop gracefully (needs_agent, insufficient context, or explicit refusal)

### 3. Running the Harness

```bash
# Local harness run
runx harness ./skills/example-validator --json

# Expected output includes:
# - case name and verdict
# - sealed receipt ID
# - observation count
```

### 4. Verifying the Receipt

```bash
runx verify --receipt receipt.json --json
```

A production-signed receipt returns `signature_mode: production` and `valid: true`.

## Real Example: Threshold Validator

This repo includes a complete working skill. Files:

```
skills/example-validator/
├── SKILL.md
├── X.yaml
├── run.py
└── fixtures/
    └── sample_input.json
```

### Install and Run

```bash
# Add the skill from registry
runx add umbtest03/example-validator@sha-<version>

# Run the harness
runx harness ./skills/example-validator --json

# Dogfood with real input
runx skill umbtest03/example-validator@sha-<version> --json \
  --input '{"score": 85, "threshold": 70}'
```

## Why Harness Matters

The harness is the difference between a demo and a verifiable skill:

1. **Automated verification** — the hosted gate runs X.yaml cases on every publish
2. **Sealed receipts** — every harness run produces a receipt that proves the skill behaved as declared
3. **Reproducible** — anyone can re-run the harness and get the same result
4. **Composable** — skills with green harnesses can be chained into larger graphs

## Resources

- [runx GitHub](https://github.com/runxhq/runx)
- [runx.ai](https://runx.ai)
- [Frantic Board](https://gofrantic.com)
- [SKILL.md Specification](https://runx.ai/docs/skill-md)
