# Knowledge Graph Snapshot API

## Endpoint

- Method: `GET`
- Path: `/api/v1/knowledgegraph`

This API returns the current Neo4j knowledge graph snapshot as structured JSON.

## Purpose

Use this API when:

- you want to inspect the current graph contents
- you want to debug imported curriculum, student, submission, or review data
- you need a compact application-level export of the graph state

## Flow

1. The client calls the snapshot endpoint with no request body.
2. The repository queries Neo4j for concepts, exercises, students, submissions, reviews, and link tables.
3. The API assembles those records into one `KnowledgeGraphDocument`.
4. The API returns the snapshot as structured JSON.

## Response Schema

```json
{
  "graph": {
    "concepts": [
      {
        "concept_id": "string",
        "name": "string",
        "description": "string",
        "difficulty": 1
      }
    ],
    "concept_relations": [
      {
        "prerequisite_id": "string",
        "concept_id": "string",
        "strength": 1.0
      }
    ],
    "exercises": [
      {
        "exercise_id": "string",
        "title": "string",
        "description": "string",
        "content": "string",
        "difficulty": "string",
        "tags": ["string"]
      }
    ],
    "exercise_concept_links": [
      {
        "exercise_id": "string",
        "concept_id": "string",
        "weight": 1.0
      }
    ],
    "exercise_path_links": [
      {
        "exercise_id": "string",
        "concept_id": "string",
        "path": "REINFORCE",
        "weight": 1.0
      }
    ],
    "exercise_relations": [
      {
        "exercise_id": "string",
        "related_exercise_id": "string",
        "weight": 1.0,
        "relation_type": "SIMILAR_PRACTICE",
        "target_concept_id": "string",
        "shared_concept_ids": ["string"],
        "difficulty_gap": 0.0,
        "progression_score": 0.7,
        "similarity_score": 0.8
      }
    ],
    "students": [
      {
        "student_id": "string",
        "current_concept": "string",
        "notes": "string"
      }
    ],
    "submissions": [
      {
        "submission_id": "string",
        "student_id": "string",
        "exercise_id": "string",
        "code": "string",
        "testcase_outputs": [
          {
            "expect": "string",
            "output": "string"
          }
        ],
        "created_at": "string"
      }
    ],
    "submission_relations": [
      {
        "previous_submission_id": "string",
        "next_submission_id": "string",
        "student_id": "string",
        "linked_at": "string",
        "same_exercise": true,
        "improvement_ratio": 0.5,
        "regression_ratio": 0.0
      }
    ],
    "reviews": [
      {
        "review_id": "string",
        "student_id": "string",
        "exercise_id": "string",
        "submission_id": "string",
        "current_concept": "string",
        "created_at": "string",
        "summary": "string",
        "detail": "string"
      }
    ],
    "review_relations": [
      {
        "previous_review_id": "string",
        "next_review_id": "string",
        "student_id": "string",
        "linked_at": "string",
        "same_concept": true,
        "improvement_signal": 0.4,
        "severity_change": -0.25
      }
    ]
  }
}
```

## Notes

- This endpoint is read-only.
- The response is built from repository queries over Neo4j, not from a cached file.
- It is useful for validating whether path-based upserts have produced the expected graph entities and relationships.
- `exercise_relations` contains outgoing `RELATED_TO` links from the main exercise to each related exercise, including relation type and recommendation-ranking metadata.
- `submission_relations` contains outgoing `NEXT_ATTEMPT` links between submissions, including improvement and regression scores.
- `review_relations` contains outgoing `NEXT_REVIEW_OF` links between adjacent reviews, including recommendation-facing progress metadata.
