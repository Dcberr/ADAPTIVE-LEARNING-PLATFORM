from __future__ import annotations

import logging

from import_exercise_batch.config import ImportTopicsSettings
from import_exercise_batch.process.mainprocess.base import BaseMainProcess
from import_exercise_batch.process.subprocess.api import CodeReviewAiSubProcess


class ImportTopicsMainProcess(BaseMainProcess):
    logger = logging.getLogger(__name__)

    def __init__(self, settings: ImportTopicsSettings) -> None:
        self.settings = settings
        self.code_review_ai_subprocess = CodeReviewAiSubProcess(
            settings.code_review_ai_api.base_url,
            settings.code_review_ai_api.max_workers,
            settings.code_review_ai_api.max_retries,
            settings.code_review_ai_api.backoff_seconds,
            settings.code_review_ai_api.put_exercise_chunk_size,
            settings.code_review_ai_api.patch_exercise_relations_chunk_size,
        )

    def run(self) -> None:
        enabled_topics = [tag for tag in self.settings.tags if tag.enable]
        self.logger.info("Starting import topics batch with %s enabled topics", len(enabled_topics))
        self.code_review_ai_subprocess.import_topics(enabled_topics)
        self.code_review_ai_subprocess.patch_topic_relations(enabled_topics)
        self.logger.info("Finished import topics batch with %s enabled topics", len(enabled_topics))
