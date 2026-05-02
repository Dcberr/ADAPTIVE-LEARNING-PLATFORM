import unittest

from code_review_ai.config.env_config import build_env_config


class EnvConfigTests(unittest.TestCase):
    def test_build_env_config_reads_qdrant_settings(self):
        settings = build_env_config(
            {
                "FIREWORKS_API_KEY": "test-key",
                "QDRANT_URL": "http://localhost:6333",
                "QDRANT_API_KEY": "qdrant-key",
                "QDRANT_COLLECTION_NAME": "exercise_index",
                "QDRANT_TIMEOUT_SECONDS": "7.5",
            }
        )

        self.assertEqual(settings.qdrant_url, "http://localhost:6333")
        self.assertEqual(settings.qdrant_api_key, "qdrant-key")
        self.assertEqual(settings.qdrant_collection_name, "exercise_index")
        self.assertEqual(settings.qdrant_timeout_seconds, 7.5)
        self.assertTrue(settings.qdrant_is_configured)


if __name__ == "__main__":
    unittest.main()
