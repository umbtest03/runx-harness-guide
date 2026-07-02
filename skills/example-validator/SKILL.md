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
Validates that input score meets threshold and returns a pass/fail verdict.
