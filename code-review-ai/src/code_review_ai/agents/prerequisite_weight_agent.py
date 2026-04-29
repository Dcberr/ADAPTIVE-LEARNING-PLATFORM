from code_review_ai.models.knowledge_graph import ConceptRecord


class PrerequisiteWeightAgent:
    """Evaluates prerequisite strength between a main concept and prerequisite concepts."""

    VALID_STRENGTHS = {1.0, 0.6, 0.3}
    DEFAULT_STRENGTH = 0.6

    def _normalize_strength(self, value: float) -> float:
        if value >= 0.8:
            return 1.0
        if value >= 0.45:
            return 0.6
        return 0.3

    def evaluate(
        self,
        *,
        main_concept: ConceptRecord,
        prerequisites: list[ConceptRecord],
    ) -> dict[str, float]:
        if not prerequisites:
            return {}

        return {
            concept.concept_id: self._score_prerequisite(
                main_concept=main_concept,
                prerequisite=concept,
            )
            for concept in prerequisites
        }

    def _score_prerequisite(
        self,
        *,
        main_concept: ConceptRecord,
        prerequisite: ConceptRecord,
    ) -> float:
        difficulty_gap = max(0, main_concept.difficulty - prerequisite.difficulty)
        difficulty_fit = 1.0 if difficulty_gap >= 1 else 0.7 if difficulty_gap == 0 else 0.3
        lexical_overlap = self._token_overlap(main_concept, prerequisite)
        name_overlap = self._name_overlap(main_concept, prerequisite)
        raw_strength = min(
            1.0,
            0.50 * difficulty_fit + 0.30 * lexical_overlap + 0.20 * name_overlap,
        )
        if prerequisite.difficulty > main_concept.difficulty:
            raw_strength = min(raw_strength, 0.3)
        return self._normalize_strength(raw_strength)

    @staticmethod
    def _token_overlap(main_concept: ConceptRecord, prerequisite: ConceptRecord) -> float:
        main_tokens = PrerequisiteWeightAgent._tokens(
            f"{main_concept.name} {main_concept.description}"
        )
        prerequisite_tokens = PrerequisiteWeightAgent._tokens(
            f"{prerequisite.name} {prerequisite.description}"
        )
        if not main_tokens or not prerequisite_tokens:
            return 0.0
        union = main_tokens | prerequisite_tokens
        if not union:
            return 0.0
        return len(main_tokens & prerequisite_tokens) / len(union)

    @staticmethod
    def _name_overlap(main_concept: ConceptRecord, prerequisite: ConceptRecord) -> float:
        main_name = main_concept.name.strip().lower()
        prerequisite_name = prerequisite.name.strip().lower()
        if not main_name or not prerequisite_name:
            return 0.0
        if main_name == prerequisite_name:
            return 1.0
        if prerequisite_name in main_name or main_name in prerequisite_name:
            return 0.7
        return 0.0

    @staticmethod
    def _tokens(value: str) -> set[str]:
        return {
            token
            for token in value.lower().replace("-", " ").replace("_", " ").split()
            if len(token) >= 3
        }
