# Knowledge Graph Design

## Overview

This document defines a practical knowledge-graph design for the current learning system.

Current entities:

- `Student`
- `Exercise`
- `Concept`
- `Review`
- `Submission`

Recommended design choice:

- merge `Student` and current `StudentProfile` into a single `Student` node

This keeps recommendation queries simpler because the student's latest learning state is stored directly on the student.

At the same time, recommendation quality improves a lot when concept-level progress is stored on relationships, not only on the global student node.

## Nodes

### Student

Represents the learner and the learner's current profile state.

Suggested properties:

- `student_id`
- `current_concept`
- `concept_mastery`
- `implementation_consistency`
- `debugging_independence`
- `efficiency_awareness`
- `concept_transfer`
- `learning_velocity`
- `profile_notes`

Purpose:

- keep broad learner-level signals that are not tied to one concept
- support overall recommendation tone, pacing, and support level

### Submission

Represents one concrete student attempt on an exercise.

Suggested properties:

- `submission_id`
- `student_id`
- `exercise_id`
- `code`
- `testcase_outputs_json`
- `created_at`

### Review

Represents structured feedback generated from one submission.

Suggested properties:

- `review_id`
- `summary`
- `detail`
- `review_items_json`
- `scorecard_json`
- `created_at`

### Exercise

Represents one learning task or programming exercise.

Suggested properties:

- `exercise_id`
- `title`
- `description`
- `content`
- `difficulty`
- `tags`

### Concept

Represents one programming concept in the curriculum.

Suggested properties:

- `concept_id`
- `name`
- `description`
- `difficulty`

## Relationship Categories

This section groups relationships by function. For each relationship, the recommended weighted properties and the meaning of those weights are listed explicitly.

## Identity And Ownership Relationships

### `(:Student)-[:SUBMITTED]->(:Submission)`

Purpose:

- track all attempts made by a student
- support progression analysis across submissions

Weights:

- no weight recommended

Meaning:

- this is an ownership link, not a ranking signal
- recommendation should read attempt quality from submission and review data, not from this edge

### `(:Submission)-[:FOR_EXERCISE]->(:Exercise)`

Purpose:

- identify which exercise a submission belongs to
- connect attempt history to exercise metadata

Weights:

- no weight recommended

Meaning:

- this is an identity relation
- the exercise match should be exact, not scored

### `(:Submission)-[:RECEIVED_REVIEW]->(:Review)`

Purpose:

- connect a submission to the generated feedback for that exact attempt

Optional reverse edge:

- `(:Review)-[:REVIEWS_SUBMISSION]->(:Submission)`

Weights:

- no weight recommended

Meaning:

- this is an exact linkage between one attempt and one review
- review severity should stay in the review payload, not on the edge

## Curriculum Relationships

### `(:Exercise)-[:TESTS]->(:Concept)`

Purpose:

- define which concepts are evaluated by an exercise
- enable recommendation by concept weakness or mastery

Weights:

- `weight`

Meaning of weight:

- `weight` is the importance of the concept within that exercise
- high `weight` means the concept is central to the exercise
- low `weight` means the concept is secondary or only lightly involved

Suggested scale:

- `1.0` for the main concept
- `0.5` to `0.8` for important supporting concepts
- `0.1` to `0.4` for minor supporting concepts

### `(:Concept)-[:PREREQUISITE_OF]->(:Concept)`

Purpose:

- model curriculum progression
- support `NEXT_CONCEPT` recommendation

Weights:

- optional `strength`

Meaning of weight:

- `strength` represents how necessary the prerequisite is
- high `strength` means the prerequisite is required before moving on
- low `strength` means the prerequisite is helpful but not strictly blocking

Suggested scale:

- `1.0` for strict prerequisite
- `0.5` to `0.8` for strong supporting prerequisite
- `0.1` to `0.4` for optional background knowledge

## Student Learning Relationships

### Student to Concept

- `(:Student)-[:HAS_CONCEPT_STATE]->(:Concept)`

Purpose:

- store concept-specific learning state for recommendation
- support reinforcement, improvement, and next-concept ranking with direct evidence
- avoid over-relying on one global student profile for all concepts

Weights:

- `mastery_score`
- `struggle_score`
- `confidence`
- `evidence_count`
- `updated_at`

Meaning of weights:

- `mastery_score`: `0.0` to `1.0`
- `struggle_score`: `0.0` to `1.0`
- `confidence`: how reliable the score is based on available evidence
- `evidence_count`: number of reviews/submissions contributing to the relation

Suggested interpretation:

- high `mastery_score` and low `struggle_score` means the student is likely ready to move forward
- high `struggle_score` means the student likely needs `REINFORCE`
- medium `mastery_score` with medium `struggle_score` often maps to `IMPROVE`

Optional derived shortcut relations:

- `(:Student)-[:MASTERED]->(:Concept)`
- `(:Student)-[:STRUGGLES_WITH]->(:Concept)`

Purpose:

- these can be derived from `HAS_CONCEPT_STATE` thresholds
- they are useful for simple queries, but the weighted state relation should be treated as the source of truth

Suggested thresholds:

- create or interpret `MASTERED` when `mastery_score >= 0.75` and `struggle_score < 0.35`
- create or interpret `STRUGGLES_WITH` when `struggle_score >= 0.60`

### Student to Exercise Solved State

- `(:Student)-[:SOLVED]->(:Exercise)`

Purpose:

- distinguish successful completion from mere attempt history
- support recommendation filtering for already-completed exercises

Weights:

- `score`
- `attempt_count`
- `solved_at`

Meaning of weights:

- `score`: how strongly the exercise was solved, not just whether it was solved
- `attempt_count`: how many tries were needed before solving
- `solved_at`: when the solve state was last reached

Suggested scale:

- `score` near `1.0` means strong solve quality
- `score` near `0.5` means barely solved or solved with weak evidence
- higher `attempt_count` means the solve may need more caution in progression decisions

### `(:Student)-[:ATTEMPTED]->(:Exercise)`

Purpose:

- record exercise exposure at the student level
- exclude already attempted exercises from recommendation

Weights:

- `attempt_count`
- `last_attempt_at`
- `best_result`

Meaning of weights:

- `attempt_count`: how many times the student tried the exercise
- `last_attempt_at`: recency of exposure
- `best_result`: the best observed result quality for that exercise

Suggested scale:

- higher `attempt_count` with low `best_result` is a strong reinforce signal
- recent `last_attempt_at` means the system should avoid immediate repetition unless reinforce is intentional

## Progression Relationships

### Submission to Submission

- `(:Submission)-[:NEXT_ATTEMPT]->(:Submission)`

Purpose:

- track how a student's attempts evolve over time
- support trend analysis and self-correction evaluation

Weights:

- `student_id`
- `linked_at`
- `same_exercise`
- `improvement_ratio`
- `regression_ratio`

Meaning of weights:

- `improvement_ratio`: how much the student improved from one submission to the next
- `regression_ratio`: how much the student regressed from one submission to the next
- `same_exercise`: whether the chain stays within the same exercise

Suggested scale:

- `improvement_ratio` near `1.0` means strong forward progress
- `regression_ratio` near `1.0` means serious backward movement

### Review to Review

- `(:Review)-[:NEXT_REVIEW_OF]->(:Review)`

Purpose:

- connect review history across attempts
- support review-based progression summaries

Weights:

- `student_id`
- `linked_at`
- `same_concept`
- `improvement_signal`
- `severity_change`

Meaning of weights:

- `improvement_signal`: overall learning improvement between reviews
- `severity_change`: change in issue severity from prior review to current review
- `same_concept`: whether the review chain stays on the same concept

Suggested scale:

- `improvement_signal` near `1.0` means clear improvement
- `improvement_signal` near `0.0` means no real progress
- `severity_change < 0` means the review got less severe
- `severity_change > 0` means the review got more severe

## Recommendation Relationships

### Exercise to Concept by Recommendation Path

- `(:Exercise)-[:RECOMMENDED_FOR {path}]->(:Concept)`

Purpose:

- pre-label exercises for recommendation intent

Example `path` values:

- `REINFORCE`
- `IMPROVE`
- `NEXT_CONCEPT`

Weights:

- `path`
- `weight`

Meaning of weights:

- some exercises fit a path much better than others even for the same concept
- recommendation can rank candidates instead of only filtering them

Suggested scale:

- `weight` near `1.0` means the exercise is a very strong fit for that path on that concept
- `weight` near `0.5` means acceptable but not ideal
- `weight` near `0.1` means weak path fit

### Student to Exercise Assignment

- `(:Student)-[:ASSIGNED {path, target_concept, sequence}]->(:Exercise)`

Purpose:

- persist recommendation results
- support roadmap tracking
- avoid recommending the same exercise repeatedly

Weights:

- `path`
- `target_concept`
- `sequence`
- `assigned_at`
- `priority`
- `reasoning_score`

Meaning of weights:

- `priority`: importance of this assigned exercise inside the roadmap
- `reasoning_score`: confidence of the recommendation engine in this assignment
- `sequence`: ordering inside the plan

## Best Practical Recommendation Setup

If you want the highest-impact weighting strategy, prioritize these first:

1. `(:Student)-[:HAS_CONCEPT_STATE]->(:Concept)` with `mastery_score`, `struggle_score`, `confidence`
2. `(:Exercise)-[:TESTS]->(:Concept)` with `weight`
3. `(:Exercise)-[:RECOMMENDED_FOR]->(:Concept)` with `path`, `weight`
4. `(:Student)-[:ATTEMPTED]->(:Exercise)` with `attempt_count`, `last_attempt_at`
5. `(:Review)-[:NEXT_REVIEW_OF]->(:Review)` with `improvement_signal`

## Recommended Minimal Graph

If you want the smallest graph that still supports a strong recommendation flow, use:

- `(:Student)-[:SUBMITTED]->(:Submission)`
- `(:Submission)-[:FOR_EXERCISE]->(:Exercise)`
- `(:Submission)-[:RECEIVED_REVIEW]->(:Review)`
- `(:Exercise)-[:TESTS]->(:Concept)`
- `(:Concept)-[:PREREQUISITE_OF]->(:Concept)`
- `(:Student)-[:ATTEMPTED]->(:Exercise)`
- `(:Student)-[:HAS_CONCEPT_STATE]->(:Concept)`
- `(:Submission)-[:NEXT_ATTEMPT]->(:Submission)`
- `(:Exercise)-[:RECOMMENDED_FOR {path}]->(:Concept)`

## How This Supports Recommendation

### Reinforce

Use:

- `STRUGGLES_WITH`
- repeated failed submissions
- low review scorecard signals
- exercises connected to the same concept through `TESTS`

Goal:

- recommend more practice on a concept the student is still weak in

### Improve

Use:

- partial progress across `NEXT_ATTEMPT`
- review links that show some improvement but incomplete correction
- medium profile scores

Goal:

- recommend exercises that deepen the same concept without moving ahead too early

### Next Concept

Use:

- `MASTERED`
- solved or successful exercise history
- prerequisite graph through `PREREQUISITE_OF`

Goal:

- move the student forward to the next concept in the curriculum

## Query Thinking

Typical recommendation questions this graph should answer:

- What concepts does this student currently struggle with?
- What concepts has this student likely mastered?
- What exercises test the student's weak concepts?
- Which exercises should be excluded because they were already attempted or assigned?
- What is the next concept after the student's current concept?
- Has the student shown improvement across recent attempts on the same exercise?

## Suggested Constraints

Recommended uniqueness constraints:

- `Student.student_id`
- `Submission.submission_id`
- `Review.review_id`
- `Exercise.exercise_id`
- `Concept.concept_id`

## Suggested Future Extensions

Optional future additions if needed:

- `TestCase` nodes if you want testcase-level concept reasoning
- `Submission.status` or `passed_test_count`
- `Review.recommendation_signal`
- `Student` relationship properties that track concept-confidence over time

## Summary

Recommended main structure:

- keep `Student` and profile merged
- keep `Submission` separate from `Review`
- connect `Submission -> Exercise -> Concept`
- connect `Student -> Concept`
- connect attempts and reviews in sequence for progression

This gives you a clean graph for:

- student state tracking
- review history analysis
- recommendation path selection
- exercise retrieval for reinforcement, improvement, and next-concept learning
