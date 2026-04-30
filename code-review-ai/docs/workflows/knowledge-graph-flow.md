# Knowledge Graph Flow

Prompt generation for knowledge-graph weighting and relation evaluation is centralized under `app/prompts/knowledge_graph/`.

## Overview

The knowledge-graph flow is split into small APIs so graph state can be written and validated incrementally.

## Curriculum Setup Flow

1. Upsert concepts with `PUT /api/v1/knowledgegraph/concepts/{concept_id}`
2. Upsert exercises with `PUT /api/v1/knowledgegraph/exercises/{exercise_id}`
3. The exercise upsert request carries exercise fields plus `concept_slugs`
4. The exercise upsert API validates those concepts and rebuilds `TESTS` and `RECOMMENDED_FOR` links
5. Patch exercise-to-exercise links with `PATCH /api/v1/knowledgegraph/exercises/{exercise_id}/relations`
6. The relation patch request carries only `related_exercise_ids`
7. The relation patch API validates those exercises and rebuilds outgoing `RELATED_TO` links for the main exercise

## Student Setup Flow

1. Upsert a student profile with `PUT /api/v1/knowledgegraph/students/{student_id}`
2. Store normalized learner-level profile scores on the `Student` node

## Submission And Review Flow

1. Upsert a submission with `PUT /api/v1/knowledgegraph/submissions/{submission_id}`
2. The submission API validates that `Student` and `Exercise` already exist
3. The submission API refreshes `SUBMITTED`, `FOR_EXERCISE`, and `NEXT_ATTEMPT` relations
4. Submission progression scores are derived later from adjacent submission testcase outputs instead of being stored on the edge
5. Upsert a review with `PUT /api/v1/knowledgegraph/reviews/{review_id}`
6. The review API validates that the referenced `Submission` exists and overwrites the stored review fields from the request
7. Review relations are refreshed to match the linked student, submission, exercise, and adjacent review-history chain

## Read Flow

1. recommendation services query the repository directly for targeted context

## Why This Split Helps

- easier validation at each write step
- clearer ownership of graph entities
- fewer oversized payloads
- simpler debugging when graph state is inconsistent

## Related Docs

- [../api/concept-api.md](/Users/thaibao/projects/review-code-app/codereviewai/docs/api/concept-api.md)
- [../api/exercise-api.md](/Users/thaibao/projects/review-code-app/codereviewai/docs/api/exercise-api.md)
- [../api/student-profile-import-api.md](/Users/thaibao/projects/review-code-app/codereviewai/docs/api/student-profile-import-api.md)
- [../api/review-import-api.md](/Users/thaibao/projects/review-code-app/codereviewai/docs/api/review-import-api.md)
