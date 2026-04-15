# Recommendation Decision Notes

## Overview

The recommendation flow no longer relies on one fixed deterministic formula set.

The current design is:

- LLM decides which extra context blocks to load
- LLM decides the recommendation path and focus concept
- Neo4j repository queries retrieve weighted candidates
- LLM filters the most important exercises into the roadmap
- LLM builds explanation blocks with structured refs

The graph still provides strong retrieval signals such as:

- `TESTS.weight`
- `RECOMMENDED_FOR.weight`
- `RELATED_TO.weight`
- `RELATED_TO.progression_score`
- `RELATED_TO.similarity_score`
- `PREREQUISITE_OF.strength`
- `NEXT_REVIEW_OF.improvement_signal`
- `NEXT_REVIEW_OF.severity_change`
- `NEXT_ATTEMPT.improvement_ratio`
- `NEXT_ATTEMPT.regression_ratio`

These weighted relations are used to fetch candidate exercises and to prepare evidence for the LLM-led decisions.

## Current Decision Stages

1. base context load
2. LLM context planning
3. conditional graph context loading
4. LLM path decision
5. graph candidate query
6. LLM roadmap selection
7. LLM explanation with refs

## Explanation Refs

The explanation response uses structured refs instead of free-form citations.

Each explanation block has:

- `content`
- `refs`

Each ref has:

- `ref_id`
- `content`
- `ref_category`

Allowed `ref_category` values:

- `code`
- `review`
- `exercise`

## Documentation Rule

If recommendation code changes:

- update `docs/workflows/recommendation-flow.md`
- update `docs/api/recommendation-api.md`
- update example response payloads
