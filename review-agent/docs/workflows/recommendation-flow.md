# Recommendation Flow

## Overview

The recommendation flow is graph-backed and starts from a minimal request:

- `student_id`
- `exercise_id`

The client does not send the full review payload. The service loads the needed context from Neo4j.

## High-Level Flow

1. The client calls `POST /api/v1/recommendation`.
2. `ReviewContextLoader` loads the latest stored review for `(student_id, exercise_id)`.
3. The same step loads recent review history through `NEXT_REVIEW_OF`.
4. The flow loads the stored `StudentProfileScoring`.
5. `ProfileScorer` computes recommendation-facing signals such as risk and readiness.
6. `GraphRAGRetriever` loads candidate exercises from Neo4j.
7. `RecommendationReasoner` selects path and candidate roadmap items.
8. `DirectiveBuilder` formats the final roadmap and stores assignment relations back into Neo4j.

## Main Inputs

- latest review
- recent review history
- student profile
- exercise-to-concept graph links
- concept prerequisite graph
- recommendation path graph links

## Main Outputs

- assigned recommendation path
- target concept
- ordered exercise roadmap
- stored `ASSIGNED` relations for the student

## Related Docs

- [../architecture.md](/Users/thaibao/projects/review-code-app/review-agent/docs/architecture.md)
- [../domain/knowledge-graph.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/knowledge-graph.md)
- [../api/review-import-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/review-import-api.md)
