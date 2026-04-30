from __future__ import annotations

from abc import ABC, abstractmethod


class BaseMainProcess(ABC):
    @abstractmethod
    def run(self) -> None:
        """Run the selected batch process."""
