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

### Submission

Represents one concrete student attempt on an exercise.

Suggested properties:

- `submission_id`
- `student_id`
- `exercise_id`
- `code`
- `failed_test_case_ids`
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

## Core Relationships

### Student to Submission

- `(:Student)-[:SUBMITTED]->(:Submission)`

Purpose:

- track all attempts made by a student
- support progression analysis across submissions

### Submission to Exercise

- `(:Submission)-[:FOR_EXERCISE]->(:Exercise)`

Purpose:

- identify which exercise a submission belongs to
- connect attempt history to exercise metadata

### Submission to Review

- `(:Submission)-[:RECEIVED_REVIEW]->(:Review)`

Purpose:

- connect a submission to the generated feedback for that exact attempt

Optional reverse edge:

- `(:Review)-[:REVIEWS_SUBMISSION]->(:Submission)`

### Exercise to Concept

- `(:Exercise)-[:TESTS {weight}]->(:Concept)`

Purpose:

- define which concepts are evaluated by an exercise
- enable recommendation by concept weakness or mastery

Suggested relationship property:

- `weight`: relative importance of the concept for that exercise

### Concept to Concept

- `(:Concept)-[:PREREQUISITE_OF]->(:Concept)`

Purpose:

- model curriculum progression
- support "next concept" recommendations

## Student Learning Relationships

### Student to Exercise

- `(:Student)-[:ATTEMPTED]->(:Exercise)`

Purpose:

- record exercise exposure at the student level
- exclude already attempted exercises from recommendation

### Student to Concept

- `(:Student)-[:MASTERED]->(:Concept)`

Purpose:

- mark concepts the student has demonstrated strong understanding of
- support progression to next concepts

- `(:Student)-[:STRUGGLES_WITH]->(:Concept)`

Purpose:

- mark concepts where the student shows repeated difficulty
- support reinforcement recommendations

Optional relationship properties:

- `strength`
- `updated_at`
- `evidence_count`

### Student to Exercise Solved State

- `(:Student)-[:SOLVED]->(:Exercise)`

Purpose:

- distinguish successful completion from mere attempt history

## Progression Relationships

### Submission to Submission

- `(:Submission)-[:NEXT_ATTEMPT]->(:Submission)`

Purpose:

- track how a student's attempts evolve over time
- support trend analysis and self-correction evaluation

Suggested relationship properties:

- `student_id`
- `linked_at`
- `same_exercise`

### Review to Review

- `(:Review)-[:NEXT_REVIEW_OF]->(:Review)`

Purpose:

- connect review history across attempts
- support review-based progression summaries

Suggested relationship properties:

- `student_id`
- `linked_at`
- `same_concept`

## Recommendation Relationships

### Exercise to Concept by Recommendation Path

- `(:Exercise)-[:RECOMMENDED_FOR {path}]->(:Concept)`

Purpose:

- pre-label exercises for recommendation intent

Example `path` values:

- `REINFORCE`
- `IMPROVE`
- `NEXT_CONCEPT`

### Student to Exercise Assignment

- `(:Student)-[:ASSIGNED {path, target_concept, sequence}]->(:Exercise)`

Purpose:

- persist recommendation results
- support roadmap tracking
- avoid recommending the same exercise repeatedly

Suggested relationship properties:

- `path`
- `target_concept`
- `sequence`
- `assigned_at`

## Recommended Minimal Graph

If you want the smallest graph that still supports a strong recommendation flow, use:

- `(:Student)-[:SUBMITTED]->(:Submission)`
- `(:Submission)-[:FOR_EXERCISE]->(:Exercise)`
- `(:Submission)-[:RECEIVED_REVIEW]->(:Review)`
- `(:Exercise)-[:TESTS]->(:Concept)`
- `(:Concept)-[:PREREQUISITE_OF]->(:Concept)`
- `(:Student)-[:ATTEMPTED]->(:Exercise)`
- `(:Student)-[:MASTERED]->(:Concept)`
- `(:Student)-[:STRUGGLES_WITH]->(:Concept)`
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
