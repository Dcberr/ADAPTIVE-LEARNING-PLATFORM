from __future__ import annotations

from import_exercise_batch.config import Settings
from import_exercise_batch.process.main_process import MainProcess


def main() -> None:
    settings = Settings()
    MainProcess(settings).run()


if __name__ == "__main__":
    main()
