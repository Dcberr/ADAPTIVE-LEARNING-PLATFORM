from __future__ import annotations

from textwrap import dedent

from app.models.exercise_record import ExerciseRecord
from app.models.knowledge_graph import ConceptRecord


def build_exercise_weight_messages(
    main_exercise: ExerciseRecord,
    concepts: list[ConceptRecord],
    related_exercises: list[ExerciseRecord],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You evaluate CS1 curriculum graph weights.

                Choose only 1.0, 0.7, or 0.3.

                TESTS weights:
                - 1.0 = central concept
                - 0.7 = important supporting concept
                - 0.3 = minor supporting concept

                RELATED_TO weights:
                - 1.0 = very close sibling or next-step exercise
                - 0.7 = useful related practice
                - 0.3 = weak or optional relation

                RECOMMENDED_FOR paths must be one of:
                - REINFORCE
                - IMPROVE
                - NEXT_CONCEPT

                RELATED_TO relation_type must be one of:
                - SIMILAR_PRACTICE
                - NEXT_STEP
                - PREREQUISITE_REVIEW
                - SAME_CONCEPT_HARDER
                - SAME_CONCEPT_EASIER

                Return valid JSON only.
                """
            ).strip(),
        },
        {
            "role": "user",
            "content": dedent(
                f"""
                Main exercise:
                {{
                  "exercise_id": "{main_exercise.exercise_id}",
                  "title": "{main_exercise.title}",
                  "description": "{main_exercise.description}",
                  "content": "{main_exercise.content}",
                  "difficulty": "{main_exercise.difficulty}",
                  "tags": {main_exercise.tags}
                }}

                Concept candidates:
                {[
                    {
                        "concept_id": concept.concept_id,
                        "name": concept.name,
                        "description": concept.description,
                        "difficulty": concept.difficulty,
                    }
                    for concept in concepts
                ]}

                Related exercise candidates:
                {[
                    {
                        "exercise_id": exercise.exercise_id,
                        "title": exercise.title,
                        "description": exercise.description,
                        "content": exercise.content,
                        "difficulty": exercise.difficulty,
                        "tags": exercise.tags,
                    }
                    for exercise in related_exercises
                ]}

                Return JSON in exactly this shape:
                {{
                  "concepts": [
                    {{
                      "concept_id": "string",
                      "weight": 1.0,
                      "recommended_paths": [
                        {{
                          "path": "REINFORCE",
                          "weight": 0.7
                        }}
                      ],
                      "reason": "short explanation"
                    }}
                  ],
                  "related_exercises": [
                    {{
                      "exercise_id": "string",
                      "weight": 0.7,
                      "relation_type": "SIMILAR_PRACTICE",
                      "target_concept_id": "string",
                      "shared_concept_ids": ["string"],
                      "difficulty_gap": 0.0,
                      "progression_score": 0.7,
                      "similarity_score": 0.7,
                      "reason": "short explanation"
                    }}
                  ]
                }}

                Rules:
                - Only use concept_ids from the provided concept candidates.
                - Only use exercise_ids from the provided related exercise candidates.
                - Return one item for every provided concept candidate.
                - Return one item for every provided related exercise candidate.
                - For concept weights, judge how central the concept is to solving the main exercise.
                - For concept recommended_paths, choose the path labels that best fit how this exercise should be used for that concept in CS1.
                - For related exercise weights, judge conceptual overlap and teaching progression from the main exercise.
                - Use target_concept_id only from the provided concept candidates.
                - shared_concept_ids must be a subset of the provided concept candidates.
                - difficulty_gap should be negative when the related exercise is easier, positive when harder, and near zero when similar.
                - progression_score and similarity_score should be normalized to 0.0..1.0.
                """
            ).strip(),
        },
    ]
