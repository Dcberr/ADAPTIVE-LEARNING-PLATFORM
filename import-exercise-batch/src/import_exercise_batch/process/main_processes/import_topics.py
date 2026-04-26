from __future__ import annotations

import logging

from import_exercise_batch.config import ImportTopicsSettings
from import_exercise_batch.process.main_processes.base import BaseMainProcess
from import_exercise_batch.process.subprocess.api import ReviewAgentSubProcess


class ImportTopicsMainProcess(BaseMainProcess):
    logger = logging.getLogger(__name__)

    def __init__(self, settings: ImportTopicsSettings) -> None:
        self.settings = settings
        self.review_agent_subprocess = ReviewAgentSubProcess(settings.review_agent_api.base_url)

    def run(self) -> None:
        enabled_topics = [tag for tag in self.settings.tags if tag.enable]
        self.logger.info("Starting import topics batch with %s enabled topics", len(enabled_topics))
        self.review_agent_subprocess.import_topics(enabled_topics)
        self.review_agent_subprocess.patch_topic_relations(enabled_topics)
        self.logger.info("Finished import topics batch with %s enabled topics", len(enabled_topics))
