# Knowledge Graph Flow

## Overview

The knowledge-graph flow is split into small APIs so graph state can be written and validated incrementally.

## Curriculum Setup Flow

1. Upsert concepts with `PATCH /api/v1/knowledgegraph/concepts/{concept_id}`
2. Upsert exercises with `PATCH /api/v1/knowledgegraph/exercises/{exercise_id}`
3. Link exercises to concepts and recommendation paths through the exercise payload

## Student Setup Flow

1. Upsert a student profile with `PATCH /api/v1/knowledgegraph/students/{student_id}`
2. Store normalized learner-level profile scores on the `Student` node

## Submission And Review Flow

1. Upsert a submission with `PATCH /api/v1/knowledgegraph/submissions/{submission_id}`
2. The submission API validates that `Student` and `Exercise` already exist
3. Upsert a review with `PATCH /api/v1/knowledgegraph/reviews/{review_id}`
4. The review API validates that the referenced `Submission` already exists
5. Review relations are refreshed to match the linked student, submission, and exercise

## Read Flow

1. `GET /api/v1/knowledgegraph` returns the current graph snapshot
2. recommendation services query the repository directly for targeted context

## Why This Split Helps

- easier validation at each write step
- clearer ownership of graph entities
- fewer oversized payloads
- simpler debugging when graph state is inconsistent

## Related Docs

- [../api/concept-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/concept-api.md)
- [../api/exercise-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/exercise-api.md)
- [../api/student-profile-import-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/student-profile-import-api.md)
- [../api/review-import-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/review-import-api.md)
- [../api/knowledge-graph-snapshot-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/knowledge-graph-snapshot-api.md)
