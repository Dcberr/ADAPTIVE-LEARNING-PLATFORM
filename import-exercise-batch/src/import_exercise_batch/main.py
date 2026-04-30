from __future__ import annotations

import argparse
import logging
from math import e

from import_exercise_batch.config import ImportExercisesSettings, ImportTopicsSettings
from import_exercise_batch.process import (
    ImportExercisesMainProcess,
    ImportTopicsMainProcess,
)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "batch",
        nargs="?",
        default="import_exercise",
        choices=["import_exercise", "import_topic"],
    )
    args = parser.parse_args()

    if args.batch == "import_topic":
        settings = ImportTopicsSettings.from_env()
        ImportTopicsMainProcess(settings).run()
        return
    elif args.batch == "import_exercise":
        settings = ImportExercisesSettings.from_env()
        ImportExercisesMainProcess(settings).run()
        return
    else:
        logging.error("Invalid batch type: %s", args.batch)
        exit(1)


if __name__ == "__main__":
    main()
