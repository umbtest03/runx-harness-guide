# runx Harness Guide

A practical walkthrough of the runx harness testing system — SKILL.md contracts, X.yaml test cases, fixtures, sealed receipts, and the publish-verify loop. Updated for **runx-cli v0.6.14**.

## What is runx?

[runx](https://runx.ai) is an open-source runtime for policy-bounded agent skills. Skills are packaged as a three-file unit:

- **SKILL.md** — the skill contract: what inputs it reads, what outputs it seals, and how it behaves
- **X.yaml** — the machine manifest: harness test cases, runner definitions, and catalog metadata
- **runner** — the implementation (shell, Python, JS, or MCP)

Every runx run seals a receipt that anyone can verify independently. That receipt is the unit of trust on the [Frantic](https://gofrantic.com) board and in the runx ecosystem.

## The Harness Loop

```
SKILL.md  +  X.yaml  +  fixtures/  →  runx harness  →  sealed receipt
                                                         ↓
                                              runx verify --receipt
```

### 1. SKILL.md — The Contract

Every skill starts with frontmatter that declares its identity, source, and inputs:

```yaml
---
name: example-validator
description: Validates that an input score meets a configurable policy threshold
source:
  type: cli-tool
  command: python
  args:
    - run.py
  timeout_seconds: 10
  sandbox:
    profile: readonly
    cwd_policy: skill-directory
inputs:
  score:
    type: integer
    required: true
    description: The score to validate
  threshold:
    type: integer
    required: false
    description: Minimum passing score
runx:
  input_resolution:
    required:
      - score
  artifacts:
    named_emits:
      verdict: verdict
---
```

The frontmatter is machine-readable. The `source` field tells runx how to execute the skill. Skills are detected automatically:

```bash
$ runx list skills --json
```

```json
{
  "schema": "runx.list.v1",
  "items": [
    {
      "kind": "skill",
      "name": "example-validator",
      "source": "local",
      "status": "ok",
      "harness_cases": 3
    }
  ]
}
```

```bash
$ runx skill inspect ./skills/example-validator --json
```

```json
{
  "name": "example-validator",
  "description": "Validates that an input score meets a configurable policy threshold",
  "runners": ["default"],
  "status": "ok",
  "version": "0.1.0"
}
```

### 2. X.yaml — The Machine Manifest

The manifest (`X.yaml`) defines three things: **catalog** metadata, **harness** test cases, and **runners** with their input schemas. It lives alongside SKILL.md.

```yaml
skill: example-validator
version: "0.1.0"

catalog:
  kind: skill
  audience: public
  visibility: public
  role: canonical

harness:
  cases:
    - name: passes_above_threshold
      runner: default
      inputs:
        score: 85
        threshold: 70
      expect:
        status: sealed

    - name: fails_below_threshold
      runner: default
      inputs:
        score: 45
        threshold: 60
      expect:
        status: sealed

    - name: missing_required_score
      runner: default
      inputs:
        threshold: 70
      expect:
        status: stopped

runners:
  default:
    default: true
    type: cli-tool
    command: python
    args:
      - run.py
    artifacts:
      named_emits:
        verdict: verdict
    inputs:
      score:
        type: integer
        description: The score to validate
        required: true
      threshold:
        type: integer
        description: Minimum passing score
        required: false
```

**Key fields:**
- `harness.cases` — inline test cases with named inputs and expected verdicts
- `harness.cases[].expect.status` — `sealed` (must complete), `stopped` (graceful stop)
- `runners.default.inputs` — mirrors SKILL.md inputs, used by the harness to validate payloads
- `runners.default.artifacts.named_emits` — declares what the skill emits for downstream composition

### 3. Running the Harness

```bash
# Local harness run (requires signing keys for production receipts)
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

A signed receipt returns metadata about its digest, content address, and signature mode:

```json
{
  "schema": "runx.verify_verdict.v1",
  "digest": { "status": "valid" },
  "content_address": { "status": "valid" },
  "signature": { "mode": "production" }
}
```

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

### Verify the Skill Loads

```bash
# runx detects and validates the skill automatically
runx doctor --json
```

```json
{
  "schema": "runx.doctor.v1",
  "status": "success",
  "summary": { "errors": 0, "warnings": 0, "infos": 0 }
}
```

### Install from Registry

```bash
# Add the skill from the hosted registry
runx add umbtest03/example-validator@sha-<version>
```

### Local Execution

```bash
# Run the skill with specific input (requires signing keys)
runx skill ./skills/example-validator --json \
  --input '{"score": 85, "threshold": 70}'
```

## Why Harness Matters

The harness is the difference between a demo and a verifiable skill:

1. **Automated verification** — the hosted gate runs X.yaml cases on every publish
2. **Sealed receipts** — every harness run produces a receipt that proves the skill behaved as declared
3. **Reproducible** — anyone can re-run the harness and get the same result
4. **Composable** — skills with green harnesses can be chained into larger graphs

## Real Receipt Format

A sealed receipt contains the full execution audit trail:

```json
{
  "schema": "runx.receipt.v1",
  "id": "sha256:052e91300884c03daae761d64d73a8ec2381a24d6035850e80b4d39807b38951",
  "issuer": { "type": "hosted", "kid": "..." },
  "signature": { "alg": "Ed25519", "value": "base64:..." },
  "subject": {
    "kind": "skill",
    "ref": { "type": "harness", "uri": "hrn_..." }
  },
  "seal": {
    "disposition": "closed",
    "reason_code": "process_closed"
  }
}
```

## Resources

- [runx GitHub](https://github.com/runxhq/runx)
- [runx.ai](https://runx.ai)
- [Frantic Board](https://gofrantic.com)
- [SKILL.md Specification](https://runx.ai/docs/skill-md)
