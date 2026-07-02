---
name: example-validator
version: 0.1.0
description: Validates that an input score meets a configurable policy threshold
inputs:
  score:
    type: integer
    description: The score to validate
    required: true
  threshold:
    type: integer
    description: Minimum passing score
    required: false
    default: 70
outputs:
  verdict:
    type: object
    description: Pass/fail decision with reason
    properties:
      passed:
        type: boolean
      reason:
        type: string
run:
  kind: python
  file: run.py
---
