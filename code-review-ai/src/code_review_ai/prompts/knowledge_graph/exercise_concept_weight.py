from __future__ import annotations

from textwrap import dedent

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord


def build_exercise_concept_weight_messages(
    main_exercise: ExerciseRecord,
    concepts: list[ConceptRecord],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You evaluate how strongly a CS1 exercise tests each candidate concept.

                Your job is to decide whether each concept is central, supporting, or only
                loosely related to solving the exercise.

                Do not guess one coarse final weight from intuition alone.
                Instead, evaluate the exercise-concept relation on multiple dimensions and
                return normalized evidence scores.

                Think in this order before writing the JSON:
                1. Identify what the student must understand to solve the exercise correctly.
                2. Separate truly required concepts from supporting background concepts.
                3. Score each concept conservatively and consistently.
                4. Recommend the best learning path labels for how the exercise should be used.

                RECOMMENDED_FOR paths must be one of:
                - REINFORCE
                - IMPROVE
                - NEXT_CONCEPT

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

                Return JSON in exactly this shape:
                {{
                  "concepts": [
                    {{
                      "concept_id": "string",
                      "centrality_score": 0.7,
                      "solution_dependency_score": 0.7,
                      "explicit_usage_score": 0.7,
                      "difficulty_alignment_score": 0.7,
                      "recommended_paths": [
                        {{
                          "path": "REINFORCE",
                          "weight": 0.7
                        }}
                      ]
                    }}
                  ]
                }}

                Rules:
                - Only use concept_ids from the provided concept candidates.
                - Return one item for every provided concept candidate.
                - centrality_score should reflect how central the concept is to the core learning objective of the exercise.
                - solution_dependency_score should be high only when the student must understand that concept to solve the exercise correctly.
                - explicit_usage_score should be high when the concept is directly exercised in the likely implementation, not just nearby background knowledge.
                - difficulty_alignment_score should be high when the concept's difficulty level fits the exercise's role for practice and teaching.
                - For concept recommended_paths, choose the path labels that best fit how this exercise should be used for that concept in CS1.
                - All *_score fields must be normalized to 0.0..1.0.
                - Prefer lower scores when the concept is only indirectly helpful or replaceable by another more central concept.
                - Do not inflate scores just because the concept appears in tags or wording.
                - Use REINFORCE when the exercise is best as repeated practice on an already introduced concept.
                - Use IMPROVE when the exercise deepens skill on the concept but is still within the same concept family.
                - Use NEXT_CONCEPT only when the exercise is a realistic bridge into a new target concept.
                """
            ).strip(),
        },
    ]
