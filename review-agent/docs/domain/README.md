# Domain Docs

This folder contains stable domain concepts that multiple APIs and workflows depend on.

## Files

- [knowledge-graph.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/knowledge-graph.md): entities, relationship categories, and weighted graph design
- [concept-weight-rules.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/concept-weight-rules.md): detailed meaning and usage rules for concept-related weights
- [exercise-recommendation-rules.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/exercise-recommendation-rules.md): domain rules for exercise authoring, relation validation, and recommendation-facing exercise links
- [review-relationship-rules.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/review-relationship-rules.md): domain rules for review linking, partial patch behavior, and review-history progression signals
- [submission-progression-rules.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/submission-progression-rules.md): domain rules for submission linking and `NEXT_ATTEMPT` progression scoring
- [student-profile-scoring.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/student-profile-scoring.md): interpretation of normalized learner profile metrics
- [recommendation-formulas.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/recommendation-formulas.md): current path, target-concept, and candidate-ranking formulas used by recommendation

## Use This Folder When

- you need to understand what a model means, not just how an API is shaped
- you need to reason about graph relations or recommendation signals
- you are changing storage, recommendation ranking, or profile scoring logic
