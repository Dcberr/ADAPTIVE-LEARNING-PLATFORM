import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from code_review_ai.api.knowledge_graph_deps import get_neo4j_driver
from code_review_ai.config import build_env_config


class KnowledgeGraphDependencyTests(unittest.TestCase):
    def test_get_neo4j_driver_initializes_driver_when_startup_state_is_missing(self):
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))
        settings = build_env_config(
            {
                "FIREWORKS_API_KEY": "test-key",
                "NEO4J_URI": "bolt://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "password",
            }
        )
        fake_driver = object()

        with patch(
            "code_review_ai.api.knowledge_graph_deps.get_env_config",
            return_value=settings,
        ), patch(
            "code_review_ai.api.knowledge_graph_deps.GraphDatabase.driver",
            return_value=fake_driver,
        ) as driver_factory:
            driver = get_neo4j_driver(request)

        self.assertIs(driver, fake_driver)
        self.assertIs(request.app.state.neo4j_driver, fake_driver)
        driver_factory.assert_called_once_with(
            "bolt://localhost:7687",
            auth=("neo4j", "password"),
        )

    def test_get_neo4j_driver_returns_existing_driver_from_app_state(self):
        existing_driver = object()
        request = SimpleNamespace(
            app=SimpleNamespace(state=SimpleNamespace(neo4j_driver=existing_driver))
        )

        driver = get_neo4j_driver(request)

        self.assertIs(driver, existing_driver)

    def test_get_neo4j_driver_raises_http_503_when_neo4j_is_not_configured(self):
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))
        settings = build_env_config(
            {
                "FIREWORKS_API_KEY": "test-key",
            }
        )

        with patch(
            "code_review_ai.api.knowledge_graph_deps.get_env_config",
            return_value=settings,
        ):
            with self.assertRaises(HTTPException) as context:
                get_neo4j_driver(request)

        self.assertEqual(context.exception.status_code, 503)
        self.assertIn("Neo4j is not configured", context.exception.detail)


if __name__ == "__main__":
    unittest.main()
