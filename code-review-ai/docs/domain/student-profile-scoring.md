# Student Profile Scoring

## Overview

`StudentProfileScoring` stores normalized learner-level signals on the `Student` node.

Each score uses `0.0` to `1.0`.

- `0.0` means very weak evidence
- `0.5` means mixed or developing evidence
- `1.0` means very strong evidence

## Metrics

### `concept_mastery`

- how solid the student's overall conceptual understanding is across recent evidence

### `implementation_consistency`

- how consistently the student turns ideas into correct code structure

### `debugging_independence`

- how well the student can identify and recover from mistakes without heavy support

### `efficiency_awareness`

- how aware the student is of choosing cleaner or more appropriate constructs

### `concept_transfer`

- how well the student can apply known ideas to related but slightly different tasks

### `learning_velocity`

- how quickly the student appears to improve across attempts and reviews

### `notes`

- human-readable summary or repository-generated explanation of the profile state

## Important Distinction

- `StudentProfileScoring` uses `0.0..1.0`
- review `scorecard` still uses `1..5`

This means:

- the review flow returns instructional evaluation on a `1..5` scale
- the graph stores long-lived student profile signals on a normalized `0..1` scale
