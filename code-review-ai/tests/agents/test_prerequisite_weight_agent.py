import unittest

from code_review_ai.agents.prerequisite_weight_agent import PrerequisiteWeightAgent
from code_review_ai.models.knowledge_graph import ConceptRecord


class PrerequisiteWeightAgentTests(unittest.TestCase):
    def test_prerequisite_strength_prefers_lower_level_foundations(self):
        agent = PrerequisiteWeightAgent()
        main_concept = ConceptRecord(
            concept_id="nested-loops",
            slug="nested-loops",
            name="Nested Loops",
            description="Use nested loops to traverse 2D structures",
            difficulty=2,
        )
        prerequisite = ConceptRecord(
            concept_id="loops",
            slug="loops",
            name="Loops",
            description="Use loops for repeated execution",
            difficulty=1,
        )

        strengths = agent.evaluate(
            main_concept=main_concept,
            prerequisites=[prerequisite],
        )

        self.assertIn(strengths["loops"], {0.6, 1.0})

    def test_prerequisite_strength_downgrades_harder_unrelated_concepts(self):
        agent = PrerequisiteWeightAgent()
        main_concept = ConceptRecord(
            concept_id="variables",
            slug="variables",
            name="Variables",
            description="Store simple values in variables",
            difficulty=1,
        )
        prerequisite = ConceptRecord(
            concept_id="recursion",
            slug="recursion",
            name="Recursion",
            description="Solve problems with self-calls",
            difficulty=3,
        )

        strengths = agent.evaluate(
            main_concept=main_concept,
            prerequisites=[prerequisite],
        )

        self.assertEqual(strengths["recursion"], 0.3)


if __name__ == "__main__":
    unittest.main()
