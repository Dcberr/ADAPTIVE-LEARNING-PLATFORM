# Review Agent Architecture

## Overview

This system now has three connected capabilities:

- review student code and produce structured educational feedback
- store curriculum knowledge and exercise content in Neo4j
- store student learning state in Neo4j
- generate a roadmap of multiple mandatory exercises through an LLM-led recommendation workflow over Neo4j graph context

The recommendation input is no longer required to carry the full review payload. It is built from:

- `student_id`
- `exercise_id`

The latest review context, student profile, and exercise concept are loaded from Neo4j during the recommendation flow.

The recommendation path is decided internally through LLM path selection over graph-backed context. The client does not choose `REINFORCE`, `IMPROVE`, or `NEXT_CONCEPT`.

## High-Level Flows

```text
Client
  -> POST /api/v1/review_code
  -> Review LangGraph
  -> ReviewResponse
```

```text
Client
  -> PUT /api/v1/knowledgegraph/concepts/{concept_id}
  -> Neo4j concept upsert

Client
  -> PUT /api/v1/knowledgegraph/exercises/{exercise_id}
  -> Neo4j exercise upsert

Client
  -> PUT /api/v1/knowledgegraph/students/{student_id}
  -> Neo4j student upsert

Client
  -> PUT /api/v1/knowledgegraph/submissions/{submission_id}
  -> Neo4j submission upsert

Client
  -> PUT /api/v1/knowledgegraph/reviews/{review_id}
  -> Neo4j review upsert

Client
  -> GET /api/v1/knowledgegraph
  -> Neo4j graph snapshot
```

```text
Client
  -> POST /api/v1/recommendation
  -> Recommendation LangGraph
     1. BaseContextLoader
     2. ContextPlanner
     3. ConditionalContextLoader
     4. PathDecider
     5. ExerciseCandidateRetriever
     6. RoadmapBuilder
     7. ExplanationBuilder
  -> RecommendationResponse with roadmap
```

## Runtime Components

### Application Bootstrap

File: [app/app.py](/Users/thaibao/projects/review-code-app/review-agent/app/app.py)

Startup responsibilities:

- load application settings from environment through `app/config.py`
- initialize the Fireworks-compatible `OpenAI` client
- initialize the Neo4j driver
- register review, recommendation, and knowledge graph routers

Required graph environment variables:

- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`

LLM environment variables:

- `FIREWORKS_API_KEY`
- `FIREWORKS_BASE_URL`
- `FIREWORKS_MODEL`

### API Surface

Current endpoints:

- `POST /api/v1/review_code`
- `POST /api/v1/recommendation`
- `PUT /api/v1/knowledgegraph/concepts/{concept_id}`
- `PUT /api/v1/knowledgegraph/exercises/{exercise_id}`
- `PUT /api/v1/knowledgegraph/students/{student_id}`
- `PUT /api/v1/knowledgegraph/submissions/{submission_id}`
- `PUT /api/v1/knowledgegraph/reviews/{review_id}`
- `GET /api/v1/knowledgegraph`

## Review Architecture

### Review Workflow

File: [app/services/review_code_service.py](/Users/thaibao/projects/review-code-app/review-agent/app/services/review_code_service.py)

The review pipeline uses `StateGraph(ReviewState)` with these nodes:

- `logic`
- `fix_hint`
- `review_link`
- `improve`
- `overview`
- `scoring`

Outputs of the review pipeline:

- summary paragraph
- `review_items`
- scorecard

After response assembly, the review API also persists graph context:

- generates `review_id`
- stores the `Review` node with `student_id`, `exercise_id`, and `submission_id`
- links `(:Review)-[:REVIEWS_EXERCISE]->(:Exercise)`
- recalculates or creates the `Student` profile node from the review scorecard

This stored output becomes the primary input to the recommendation system.

## Neo4j Knowledge Graph

### Storage Model

The knowledge graph is now stored in Neo4j rather than in local JSON.

Core graph entities:

- `(:Concept)`
- `(:Exercise)`
- `(:Student)`
- `(:Review)`

Core relationships:

- `(:Concept)-[:PREREQUISITE_OF]->(:Concept)`
- `(:Exercise)-[:TESTS {weight}]->(:Concept)`
- `(:Exercise)-[:RELATED_TO {weight, relation_type, target_concept_id, shared_concept_ids, difficulty_gap, progression_score, similarity_score}]->(:Exercise)`
- `(:Exercise)-[:RECOMMENDED_FOR {path}]->(:Concept)`
- `(:Student)-[:MASTERED]->(:Concept)`
- `(:Student)-[:ATTEMPTED]->(:Exercise)`
- `(:Student)-[:RECEIVED_REVIEW]->(:Review)`
- `(:Review)-[:REVIEWS_EXERCISE]->(:Exercise)`
- `(:Review)-[:NEXT_REVIEW_OF]->(:Review)`
- `(:Review)-[:RECOMMENDS {path, target_concept, sequence}]->(:Exercise)`
- `(:Student)-[:ASSIGNED {path, target_concept, sequence}]->(:Exercise)`

Important design change:

- exercises are stored directly as graph nodes with their own metadata and content
- the system no longer stores external exercise references in code as the recommendation source
- concept progression is defined by graph edges, not Python constants

### Repository Layer

File: [app/repositories/knowledge_graph_repository.py](/Users/thaibao/projects/review-code-app/review-agent/app/repositories/knowledge_graph_repository.py)

Responsibilities:

- upsert concept nodes
- upsert prerequisite edges
- upsert exercise nodes
- upsert student nodes
- upsert review nodes
- upsert exercise-to-concept edges
- upsert exercise-to-exercise related edges
- upsert exercise-to-path edges
- upsert student-to-mastered-concept edges
- upsert student attempt links
- upsert submission-to-submission attempt progression links
- link each new review to the previous review for the same student
- recalculate or create the student profile from each stored review
- retrieve recommendation context by `student_id` and `exercise_id`
- retrieve next concepts from Neo4j
- retrieve recommendation candidates from Neo4j for GraphRAG
- exclude previously attempted or assigned exercises for the same student
- persist assigned roadmap links after recommendation
- return a graph snapshot for inspection

### Knowledge Graph APIs

Concept write API:

- file: [app/api/knowledge_graph_route.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/knowledge_graph_route.py)
- endpoint: `PUT /api/v1/knowledgegraph/concepts/{concept_id}`

Concept payload:

- `name`
- `description`
- `difficulty`
- `prerequisite_ids`

Exercise write API:

- file: [app/api/knowledge_graph_route.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/knowledge_graph_route.py)
- endpoint: `PUT /api/v1/knowledgegraph/exercises/{exercise_id}`

Exercise payload:

- `title`
- `description`
- `content`
- `difficulty`
- `tags`
- `concept_ids`
- `related_exercise_ids`

Exercise write behavior:

- the client provides exercise metadata plus related entity ids
- the API validates that relation ids already exist in Neo4j before writing
- the knowledge-graph LLM evaluates `TESTS.weight`
- the knowledge-graph LLM chooses `RECOMMENDED_FOR.path` and `RECOMMENDED_FOR.weight`
- the knowledge-graph LLM evaluates `RELATED_TO` metadata including weight, relation type, shared concepts, and progression/similarity signals

Student write API:

- file: [app/api/knowledge_graph_route.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/knowledge_graph_route.py)
- endpoint: `PUT /api/v1/knowledgegraph/students/{student_id}`

Student payload:

- `student_profile`

Submission write API:

- file: [app/api/knowledge_graph_route.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/knowledge_graph_route.py)
- endpoint: `PUT /api/v1/knowledgegraph/submissions/{submission_id}`

Submission payload:

- `student_id`
- `exercise_id`
- `code`
- `testcase_outputs`

Submission write behavior:

- validates that `Student` and `Exercise` already exist
- refreshes `SUBMITTED` and `FOR_EXERCISE`
- refreshes adjacent attempt links on the same exercise with `NEXT_ATTEMPT`
- computes `improvement_ratio` and `regression_ratio` from testcase outputs

Review write API:

- file: [app/api/knowledge_graph_route.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/knowledge_graph_route.py)
- endpoint: `PUT /api/v1/knowledgegraph/reviews/{review_id}`

Review payload:

- `submission_id`
- `summary`
- `detail`
- `review_items`
- `scorecard`
- `current_concept`

Review write behavior:

- validates that the resolved `Submission` already exists
- overwrites the stored review fields from the request
- refreshes `Student -> Review`, `Submission -> Review`, `Review -> Submission`, and `Review -> Exercise`
- rebuilds adjacent `NEXT_REVIEW_OF` links with `same_concept`, `improvement_signal`, and `severity_change`

Graph read API:

- file: [app/api/knowledge_graph_route.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/knowledge_graph_route.py)
- endpoint: `GET /api/v1/knowledgegraph`

## Recommendation Architecture

### Input Contract

File: [app/api/recommendation_schema.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/recommendation_schema.py)

The recommendation request now accepts:

- `student_id`
- `exercise_id`

This means recommendation depends on stored graph context in Neo4j rather than requiring the client to pass `ReviewResponse`, student profile scoring, or current concept again.

The recommendation response returns a roadmap plus structured explanation blocks.
Recommendation loads:

- base context first from the latest review, latest submission, student profile, and current exercise
- additional context blocks only when the context-planning LLM requests them
- weighted candidate exercises from `TESTS`, `RECOMMENDED_FOR`, `RELATED_TO`, and `PREREQUISITE_OF`

### Student Profile Scoring

File: [app/models/student_profile.py](/Users/thaibao/projects/review-code-app/review-agent/app/models/student_profile.py)

The student profile scoring object captures long-lived learner signals:

- `concept_mastery`
- `implementation_consistency`
- `debugging_independence`
- `efficiency_awareness`
- `concept_transfer`
- `learning_velocity`
- `notes`

Each metric is currently normalized from `0.0` to `1.0`.

### Recommendation Scoring Framework

File: [app/models/recommendation_framework.py](/Users/thaibao/projects/review-code-app/review-agent/app/models/recommendation_framework.py)

The recommendation workflow still returns a framework object for roadmap assignment:

- `risk_level`
- `readiness_level`
- `explanation`

Framework intent:

- `risk_level`: how cautious the roadmap should be before the student advances
- `readiness_level`: whether the student should reinforce, improve, or move to a next concept

This framework is now decided during the LLM path-decision step and returned with the roadmap.

## Recommendation LangGraph

### Workflow

File: [app/services/recommendation_service.py](/Users/thaibao/projects/review-code-app/review-agent/app/services/recommendation_service.py)

The recommendation workflow uses `StateGraph(RecommendationState)` with these nodes:

- `base_context_loader`
- `context_planner`
- `conditional_context_loader`
- `path_decider`
- `candidate_retriever`
- `roadmap_builder`
- `explanation_builder`

### Node Responsibilities

`BaseContextLoader`

- loads the minimum stable graph context from Neo4j
- includes current exercise, latest review, latest submission, student profile, and tested concepts

`ContextPlanner`

- uses the LLM to decide which extra context blocks are needed
- can request:
  - `review_trend`
  - `submission_trend`
  - `exercise_graph`
  - `concept_progression`
  - `student_history`
- does not generate raw Cypher

`ConditionalContextLoader`

- fetches only the extra context blocks chosen by the LLM
- loads previous review and previous submission payloads when available so explanation can cite them later

`PathDecider`

- uses the LLM to choose one path from:
  - `REINFORCE`
  - `IMPROVE`
  - `NEXT_CONCEPT`
- also chooses the focus concept and returns `risk_level`, `readiness_level`, and an explanation

`CandidateRetriever`

- queries Neo4j for weighted candidates for the selected path and focus concept
- returns `path_weight`, `tests_weight`, `related_weight`, `progression_score`, and `similarity_score`
- filters out exercises already linked to the student through `ATTEMPTED` or `ASSIGNED`

`RoadmapBuilder`

- lets the LLM choose the most important exercises from the graph candidate list
- stores step directives
- computes graph summary metrics from the selected roadmap

`ExplanationBuilder`

- uses the LLM only after the roadmap is already selected
- generates:
  - `reasoning.content`
  - `reasoning.refs`
  - `roadmap_summary.content`
  - `roadmap_summary.refs`
- explanation refs are structured and separated from the prose

### GraphRAG Strategy

The current recommendation pattern is:

1. retrieve base graph context from Neo4j
2. let an LLM decide which extra context blocks to load
3. load only those extra context blocks from Neo4j
4. let an LLM choose the path and focus concept from the assembled context
5. query weighted graph candidates from Neo4j
6. let an LLM filter the most important exercises into the roadmap
7. let an LLM build explanation blocks with structured refs

This is an LLM-led orchestration design over constrained graph queries, not a free-form query generator.

## Data Models

### Review Models

Files:

- [app/api/review_code_schema.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/review_code_schema.py)
- [app/models/review_state.py](/Users/thaibao/projects/review-code-app/review-agent/app/models/review_state.py)

Important models:

- `ReviewRequest`
- `ReviewResponse`
- `ReviewItem`
- `ScoreCard`
- `ReviewState`

### Recommendation Models

Files:

- [app/api/recommendation_schema.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/recommendation_schema.py)
- [app/models/recommendation_state.py](/Users/thaibao/projects/review-code-app/review-agent/app/models/recommendation_state.py)
- [app/models/recommendation_framework.py](/Users/thaibao/projects/review-code-app/review-agent/app/models/recommendation_framework.py)
- [app/models/student_profile.py](/Users/thaibao/projects/review-code-app/review-agent/app/models/student_profile.py)

Important models:

- `RecommendationRequest`
- `RecommendationResponse`
- `RecommendationExercise`
- `RecommendationRoadmapStep`
- `RecommendationState`
- `RecommendationScoringFramework`
- `StudentProfileScoring`
- `StudentRecord`

### Knowledge Graph Models

Files:

- [app/models/exercise_record.py](/Users/thaibao/projects/review-code-app/review-agent/app/models/exercise_record.py)
- [app/models/knowledge_graph.py](/Users/thaibao/projects/review-code-app/review-agent/app/models/knowledge_graph.py)
- [app/api/knowledge_graph_schema.py](/Users/thaibao/projects/review-code-app/review-agent/app/api/knowledge_graph_schema.py)

Important models:

- `ExerciseRecord`
- `ConceptRecord`
- `ConceptRelation`
- `ExerciseConceptLink`
- `ExercisePathLink`
- `ExerciseRelation`
- `KnowledgeGraphDocument`
- `StudentRecord`

## End-to-End Flow

### 1. Review

1. Client submits code and assignment/test context.
2. Review LangGraph produces `ReviewResponse`.
3. The review is stored in Neo4j and linked to the student.
4. The latest prior review is linked to the new review with `NEXT_REVIEW_OF`.

### 2. Graph Authoring

1. Curriculum or admin services insert concepts into Neo4j.
2. Curriculum or admin services insert exercises into Neo4j.
3. Student records can be inserted or updated in Neo4j.
4. Each exercise is linked to concepts, supported recommendation paths, and curated related exercises.

### 3. Recommendation

1. Client submits:
   - `student_id`
   - `exercise_id`
2. The recommendation service loads base context from Neo4j.
3. The context-planning LLM decides which additional context blocks are needed.
4. The service loads only those selected graph context blocks.
5. The path-decision LLM chooses the pedagogical path and focus concept.
6. Neo4j returns weighted candidate exercises for that path and concept.
7. The roadmap-building LLM filters the most important exercises and writes directives.
8. The explanation LLM returns structured explanation blocks with refs.
9. The assigned roadmap is stored back into Neo4j and linked to the review that produced it.

## Directory Map

```text
app/
  agents/      Review analysis agents
  api/         FastAPI routes, schemas, dependencies
  models/      Review, graph, profile, and recommendation models
  services/    Review LangGraph, Neo4j repository, recommendation LangGraph
  utils/       Shared parsing and logging helpers
docs/
  architecture.md
main.py
```

## Current Characteristics

- review remains LLM-powered
- recommendation is now both LangGraph-powered and Neo4j-backed
- path assignment is LLM-decided from assembled graph context
- roadmap generation is graph-grounded
- roadmap responses expose graph-backed `focus_concept_id`
- roadmap exercises expose `concept_ids` and `directive` without per-step `focus`, `path`, or `target_concept`
- explanation responses expose separate structured refs with `code`, `review`, and `exercise` categories
- student profile scoring is a first-class input
- student state is persisted and reused across recommendations
- review history is linked and reused across recommendations
- exercise content is stored in the graph

## Notes

- the recommendation service now depends on both Fireworks-compatible LLM access and Neo4j connectivity
- recommendation quality depends on Neo4j being populated with concept and exercise data
- `docs/workflow.mermaid` is still absent from the workspace, although the review workflow exists in code
