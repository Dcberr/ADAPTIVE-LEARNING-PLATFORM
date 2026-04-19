# Review Agent Documentation

## Overview

This document describes the current review-agent flow used by `POST /api/v1/review_code`.

The review system is a LangGraph-based multi-agent workflow for CS1 code review. It takes student code, failing testcase results, and an optional `history` array sorted by time descending, then returns:

- a beginner-friendly summary
- structured review items
- per-error links to the latest previous attempt when the same testcase failed before
- a scorecard with ten learning signals

Prompt generation for the review flow is centralized under `app/prompts/review/`. Each prompt file matches one review function, such as `logic.py`, `fix_hint.py`, `review_link.py`, `overview.py`, and `scoring.py`.

## Endpoint

- Route: `POST /api/v1/review_code`
- Route implementation: `app/api/review_code_route.py`
- Request schema: `app/api/review_code_schema.py::ReviewRequest`
- Response schema: `app/api/review_code_schema.py::ReviewResponse`

## Request Schema

```json
{
  "assignment": {
    "content": "string",
    "language": "string"
  },
  "code": "string",
  "test_results": [
    {
      "testcase_id": "uuid",
      "name": "string",
      "status": "string",
      "input": "string",
      "expect": "string",
      "actual": "string"
    }
  ],
  "history": [
    {
      "submission_id": "uuid",
      "code": "string",
      "failed_test_case_ids": ["uuid"],
      "passed_test_case_ids": ["uuid"]
    }
  ]
}
```

## Response Schema

```json
{
  "review_id": "string",
  "summary": "string",
  "detail": "string",
  "review_items": [
    {
      "line": {
        "start": 1,
        "end": 1
      },
      "column": {
        "start": 1,
        "end": 10
      },
      "code_snippet": "string",
      "type": "Error",
      "issue": "string",
      "fix_suggestion": "string",
      "review_link": {
        "previous_submission_id": "string",
        "previous_code_snippets": ["string"],
        "comparison_mode": "persistent",
        "what_improved": "string",
        "what_still_needs_work": "string",
        "relation_summary": "string"
      }
    }
  ],
  "scorecard": {
    "problem_solving_creativity": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "logic_traceability": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "generalization_score": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "construct_appropriateness": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "self_correction_path": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "variable_understanding": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "control_flow_understanding": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "input_output_awareness": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "edge_case_awareness": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    },
    "debugging_readiness": {
      "score": 1,
      "label": "string",
      "explanation": "string"
    }
  }
}
```

## Runtime Model Configuration

Model wiring is now centralized in:

- `app/config/model_config.py`
- `app/config/env_config.py`
- `app/api/review_code_deps.py`

The highest-level grouping is the feature name:

- `review`
- `recommendation`
- `knowledge_graph`

Within `review`, each agent stage has its own config entry:

- `logic`
- `fix_hint`
- `review_link`
- `improvement`
- `overview`
- `scoring`

Each stage config includes:

- `model_name`
- `temperature`
- `max_tokens`

Current review-stage defaults are tuned by role rather than using one shared model:

- `logic`: `fireworks/kimi-k2p5`, `temperature=0.1`, `max_tokens=2200`
- `fix_hint`: `fireworks/deepseek-v3p2`, `temperature=0.25`, `max_tokens=900`
- `review_link`: `fireworks/deepseek-v3p2`, `temperature=0.1`, `max_tokens=1000`
- `improvement`: `fireworks/kimi-k2p5`, `temperature=0.15`, `max_tokens=1200`
- `overview`: `fireworks/deepseek-v3p2`, `temperature=0.3`, `max_tokens=950`
- `scoring`: `fireworks/deepseek-v3p2`, `temperature=0.05`, `max_tokens=1800`

The shared default map lives in `app/config/model_config.py`, and environment overrides are loaded through `EnvConfig.get_stage_config(feature, stage)`.

Example review env vars:

- `REVIEW_MODEL`
- `REVIEW_LOGIC_MODEL`
- `REVIEW_LOGIC_TEMPERATURE`
- `REVIEW_LOGIC_MAX_TOKENS`
- `REVIEW_FIX_HINT_MODEL`
- `REVIEW_SCORING_MODEL`

If a stage-specific env var is not set, the loader falls back in this order:

1. stage default from `app/config/model_config.py`
2. feature-level `REVIEW_MODEL`

## Workflow Graph

Graph definition lives in `app/services/review_code_service.py`.

Current flow:

1. `logic`
2. `fix_hint`
3. `review_link`
4. `improve`
5. `overview`
6. `scoring`

Routing behavior:

- Entry point is always `logic`
- If `logic_issues` is not empty, route to `fix_hint`
- If there are no logic issues, route directly to `improve`
- After `fix_hint`, always go to `review_link`
- After `review_link`, always go to `improve`
- After `improve`, always go to `overview`
- After `overview`, always go to `scoring`

## ReviewState

Shared workflow state lives in `app/models/review_state.py`.

Important fields:

- `code`: current student code
- `assignment_language`: assignment language
- `sandbox_results`: normalized failing testcase results
- `assignment_requirements`: assignment prompt/content
- `history`: past submissions sorted newest first, each with failed and passed testcase ids
- `previous_failed_test_case_ids`: failed testcase ids from the newest history entry
- `persistent_failed_test_case_ids`: current failures also present in the newest history entry
- `fixed_test_case_ids`: failures from the newest history entry that are now fixed
- `regressed_test_case_ids`: new failures compared with the newest history entry
- `logic_issues`: structured current logic issues keyed by testcase id
- `improvement_notes`: style/quality warnings
- `review_links`: internal cross-attempt links for logic issues
- `overview`: final teacher-style summary
- `review_items`: final merged review items
- `scorecard`: final scoring output

## Agent Details

### 1. LogicAgent

- File: `app/agents/logic_agent.py`
- Purpose: detect logic problems from failing sandbox results and map each failure to either an exact buggy snippet or the nearest relevant anchor snippet

Inputs:

- `code`
- `sandbox_results`
- progress-derived fields such as `persistent_failed_test_case_ids` and `regressed_test_case_ids`

Outputs:

- updates `logic_issues`
- fills `history_status` for each logic issue
- fills richer diagnosis fields such as `cause_type`, `why_test_failed`, `anchor_snippet`, and `missing_behavior`

Core logic:

- filters out cases where normalized `expected == actual`
- batches testcase analysis with `batch_size = 5`
- builds a compact C++ code context before prompting
- tries structural chunks from `tree-sitter` for C++ when that optional parser package is available
- falls back to C++ keyword windows when `tree-sitter` is unavailable
- prompts the model with code context and failing tests
- parses JSON into `logic_issues`
- if parsing fails or the model returns nothing, creates deterministic fallback issues

Notes:

- `evidence` in each logic issue is the testcase id
- `code_snippet` should contain verbatim buggy code only when the bug exists in the current code
- `anchor_snippet` should contain the nearest related code when the actual problem is missing logic
- `history_status` is one of:
  - `persistent`
  - `regression`
  - `current_only`

### 2. FixHintAgent

- File: `app/agents/fix_hint_agent.py`
- Purpose: generate beginner-friendly fix guidance for each current logic issue

Inputs:

- `logic_issues`
- `assignment_requirements`
- `code`
- testcase details from `sandbox_results`

Outputs:

- adds or updates `fix_suggestion` inside each logic issue

Core logic:

- builds one prompt per logic issue
- runs those per-issue LLM calls asynchronously with bounded concurrency inside the node
- prompts using assignment, current code, current issue summary, testcase details, `cause_type`, `why_test_failed`, `missing_behavior`, and `anchor_snippet`
- chooses a different hint strategy depending on whether the issue is `incorrect_code`, `missing_logic`, `missing_branch`, or `missing_validation`
- asks for one small, actionable next step instead of a full rewrite
- does not use the previous submission directly
- uses a deterministic fallback hint when model output is invalid

### 3. ReviewLinkAgent

- File: `app/agents/review_link_agent.py`
- Purpose: compare a current issue with previous attempts that failed the same testcase and describe progress

Inputs:

- `logic_issues`
- `history`
- `code`

Outputs:

- fills `review_links`

Core logic:

- checks each logic issue by testcase id
- scans history newest first and picks the first earlier submission whose `failed_test_case_ids` contains the testcase id
- skips review-link generation when `history` is empty or when no earlier failed submission mentions the testcase
- batches link-analysis candidates with `batch_size = 5`
- prompts the model with:
  - current issue summary
  - current logic-agent code snippet or anchor snippet
  - the first earlier failed submission for that testcase
- returns a `ReviewLink` structure for each matched issue
- uses fallback link generation if parsing or the model call fails

ReviewLink meaning:

- `previous_submission_id`: id of the first earlier submission where the same testcase failed
- `previous_code_snippets`: short related snippet list from that earlier failed submission
- `comparison_mode`: usually `persistent` or `historical_match`
- `what_improved`: what changed positively
- `what_still_needs_work`: what remains unresolved
- `relation_summary`: compact relationship summary

### 4. ImprovementAgent

- File: `app/agents/improvement_agent.py`
- Purpose: detect non-correctness issues such as readability, structure, naming, and maintainability

Inputs:

- `code`

Outputs:

- fills `improvement_notes`

Core logic:

- one model call for the whole submission
- builds structured C++ code context before prompting
- prefers structural chunks from `tree-sitter` for C++ when available and otherwise falls back to keyword windows
- adds lightweight code-quality hotspot hints so the model focuses on high-signal CS1 warnings
- asks only for style/quality feedback
- explicitly excludes logic and syntax errors
- returns warning-like notes with location, snippet, issue, and suggestion
- avoids speculative "future bug" warnings unless the code structure itself clearly supports the concern

### 5. OverviewAgent

- File: `app/agents/overview_agent.py`
- Purpose: create the final student-facing summary and merge final review items

Inputs:

- `logic_issues`
- `review_links`
- `improvement_notes`
- `history`
- progress summary fields
- `code`

Outputs:

- fills `review_items`
- fills `overview`

Core logic:

- converts logic issues into `Error` review items
- attaches `review_link` to each error item by testcase id
- converts improvement notes into `Warning` review items with `review_link = None`
- prompts the model to produce a concise teacher-style overview based on:
  - code
  - history
  - progress summary
  - logic issues
  - review links
  - improvement notes

### 6. ScoringAgent

- File: `app/agents/scoring_agent.py`
- Purpose: produce a higher-level learning profile from the current code, sorted submission history, and review findings

Inputs:

- `code`
- `history`
- `overview`
- `logic_issues`
- `improvement_notes`
- progress summary fields

Outputs:

- fills `scorecard`

Score dimensions:

1. `problem_solving_creativity`
2. `logic_traceability`
3. `generalization_score`
4. `construct_appropriateness`
5. `self_correction_path`
6. `variable_understanding`
7. `control_flow_understanding`
8. `input_output_awareness`
9. `edge_case_awareness`
10. `debugging_readiness`

Core logic:

- one model call for the final scorecard
- heavily uses sorted history for `self_correction_path`
- uses rubric-anchored scoring rules with explicit evidence mapping per scorecard dimension
- tells the model to score each dimension independently instead of letting one large bug lower every score
- normalizes the returned structure against a fixed template
- falls back to a default score template on failure

## How Request Data Becomes Final Output

1. `review_code_route.py` converts API input into `ReviewState`
2. `create_initial_state()` computes progress signals from current failures and the newest history entry
3. `ReviewCodeService.review_code()` runs the LangGraph workflow
4. `OverviewAgent` assembles final `review_items`
5. `review_code_route.py` converts internal state into `ReviewResponse`

## Internal Output Mapping

### Logic issues to review items

- source: `logic_issues`
- become: `review_items` with `type = "Error"`

### Improvement notes to review items

- source: `improvement_notes`
- become: `review_items` with `type = "Warning"`

### Review links to review items

- source: `review_links`
- attached to: matching error `review_items` using testcase id

## Batching Behavior

Current batching:

- `LogicAgent`: batched by testcase, size `5`
- `ReviewLinkAgent`: batched by issue-to-history comparison, size `5`

Not currently batched:

- `ImprovementAgent`: one model call for the whole submission
- `OverviewAgent`: one model call for the whole submission
- `ScoringAgent`: one model call for the whole submission

Async per-issue work:

- `FixHintAgent`: one async model call per logic issue, with bounded concurrency inside the node

## Performance Notes

Current latency usually comes from:

- many sequential agent stages
- repeated large prompts containing current code and testcase history context
- per-issue calls in `FixHintAgent`
- a large final prompt in `OverviewAgent`
- a large final prompt in `ScoringAgent`

If the system needs optimization in the future, the first places to inspect are:

- `FixHintAgent`
- `OverviewAgent`
- `ScoringAgent`

## Files Related to the Review Agent

API and dependencies:

- `app/api/review_code_route.py`
- `app/api/review_code_schema.py`
- `app/api/review_code_deps.py`

Workflow:

- `app/services/review_code_service.py`

Agents:

- `app/agents/logic_agent.py`
- `app/agents/fix_hint_agent.py`
- `app/agents/review_link_agent.py`
- `app/agents/improvement_agent.py`
- `app/agents/overview_agent.py`
- `app/agents/scoring_agent.py`

State and support models:

- `app/models/review_state.py`
- `app/models/logic_issue.py`
- `app/models/improvement_note.py`
- `app/models/review_link.py`
- `app/models/sandbox_result.py`

Utilities:

- `app/utils/parse_json_response.py`
- `app/utils/debug_logging.py`
