from __future__ import annotations

from textwrap import dedent

from code_review_ai.models.exercise_record import ExerciseRecord
from code_review_ai.models.knowledge_graph import ConceptRecord


def build_exercise_relation_weight_messages(
    main_exercise: ExerciseRecord,
    concepts: list[ConceptRecord],
    related_exercises: list[ExerciseRecord],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": dedent(
                """
                You evaluate related-exercise edges in a CS1 curriculum graph.

                Your job is to judge whether each candidate exercise is truly related to the
                main exercise in a way that is useful for teaching, sequencing, or reinforcement
                in an introductory programming curriculum.

                Return structured evidence for both exercise similarity and exercise progression.

                Do not guess a coarse final edge strength from intuition alone.
                Instead, evaluate the pair on multiple dimensions and return normalized scores.

                Think in this order before writing the JSON:
                1. Identify the likely core learning objective of the main exercise.
                2. Compare each candidate exercise on concept overlap, problem structure,
                   implementation pattern, and difficulty progression.
                3. Decide whether the relation is mainly parallel practice, easier review,
                   harder follow-up, or a genuine next-step progression.
                4. Score each dimension conservatively and consistently.

                RELATED_TO relation_type must be one of:
                - SIMILAR_PRACTICE
                - NEXT_STEP
                - PREREQUISITE_REVIEW
                - SAME_CONCEPT_HARDER
                - SAME_CONCEPT_EASIER

                Interpretation guide:
                - SIMILAR_PRACTICE: same or nearly same target skill, mainly useful as alternative practice
                - NEXT_STEP: builds naturally on the main exercise by adding one meaningful new requirement
                - PREREQUISITE_REVIEW: candidate is simpler background practice needed before returning to the main exercise
                - SAME_CONCEPT_HARDER: same central concept, clearly harder instance or extension
                - SAME_CONCEPT_EASIER: same central concept, clearly easier or more scaffolded instance

                Strong relations should usually have at least one of these properties:
                - high overlap in central concepts
                - very similar solution pattern
                - clean pedagogical progression
                - same concept family with a meaningful difficulty step

                Weak relations should usually look like this:
                - only shallow tag overlap
                - same broad topic but different solving pattern
                - similar wording but different learning objective
                - progression that is too large, too small, or directionally unclear

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
                  "related_exercises": [
                    {{
                      "exercise_id": "string",
                      "relation_type": "SIMILAR_PRACTICE",
                      "difficulty_gap": 0.0,
                      "solution_pattern_score": 0.7,
                      "difficulty_alignment_score": 0.7,
                      "progression_score": 0.7,
                      "similarity_score": 0.7
                    }}
                  ]
                }}

                Rules:
                - Only use exercise_ids from the provided related exercise candidates.
                - Return one item for every provided related exercise candidate.
                - Judge conceptual overlap, solution similarity, and teaching progression from the main exercise.
                - difficulty_gap should be negative when the related exercise is easier, positive when harder, and near zero when similar.
                - solution_pattern_score should reflect similarity in likely implementation strategy and problem structure.
                - difficulty_alignment_score should be high when the pair has an appropriate difficulty distance for the chosen relation_type.
                - progression_score and similarity_score should be normalized to 0.0..1.0.
                - All *_score fields must be normalized to 0.0..1.0.
                - Use relation_type=SIMILAR_PRACTICE when the main value is parallel practice on very similar skills.
                - Use relation_type=NEXT_STEP when the related exercise is a natural progression from the main exercise.
                - Use relation_type=SAME_CONCEPT_HARDER or SAME_CONCEPT_EASIER when the core concept is the same but the difficulty differs meaningfully.
                - Prefer lower scores when the evidence is mixed or ambiguous.
                - Do not inflate similarity_score just because two exercises share broad tags like arrays, loops, or input-output.
                - Give high solution_pattern_score only when the likely student reasoning and implementation structure are meaningfully similar.
                - Give high progression_score only when a teacher would realistically assign the candidate immediately before or after the main exercise.
                - If the candidate mostly revisits prerequisite mechanics needed by the main exercise, prefer PREREQUISITE_REVIEW.
                - If the candidate adds one clean new twist while preserving the main core skill, prefer NEXT_STEP.
                - If relation_type is SAME_CONCEPT_HARDER or SAME_CONCEPT_EASIER, difficulty_alignment_score should usually be moderate to high.
                """
            ).strip(),
        },
    ]
