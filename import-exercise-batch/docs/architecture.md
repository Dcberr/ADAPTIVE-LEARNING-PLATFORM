# Architecture

## Overview

This project is a Python batch job built with `uv` and packaged from the root project.

The batch flow is:

1. truncate `tmp_import_exercises`
2. fetch exercises from the LeetCode GraphQL API
3. insert rows into `tmp_import_exercises`
4. compare temp data with `latest_import_exercises`
5. call a downstream update step for changed exercises
6. upsert changed rows into `latest_import_exercises`

## Project Structure

### Application Code

Handwritten application code lives in [`src/import_exercise_batch`](</Users/thaibao/projects/review-code-app/import-exercise-batch/src/import_exercise_batch>).

Important modules:

- [`main.py`](</Users/thaibao/projects/review-code-app/import-exercise-batch/src/import_exercise_batch/main.py:1>) is the CLI entrypoint
- [`config.py`](</Users/thaibao/projects/review-code-app/import-exercise-batch/src/import_exercise_batch/config.py:1>) stores runtime settings
- [`model/`](</Users/thaibao/projects/review-code-app/import-exercise-batch/src/import_exercise_batch/model>) contains domain models such as `Exercise`
- [`process/main_process.py`](</Users/thaibao/projects/review-code-app/import-exercise-batch/src/import_exercise_batch/process/main_process.py:1>) orchestrates the batch flow
- [`process/subprocess/`](</Users/thaibao/projects/review-code-app/import-exercise-batch/src/import_exercise_batch/process/subprocess>) contains class-based subprocess units

### Generated Client Code

Generated OpenAPI client code lives in [`libs/clients/codereviewapi`](</Users/thaibao/projects/review-code-app/import-exercise-batch/libs/clients/codereviewapi>).

This location was chosen so generated code is separated from handwritten application code.

Reasons:

- generated files can be replaced safely during regeneration
- app code in `src/` stays focused on business logic
- future generated clients can live beside this one under `libs/clients/`
- the repo keeps a cleaner monorepo-style structure

## Why Not Put Generated Code In `src/`

We do not place generated client code inside `src/import_exercise_batch` because:

- generated files change often
- regeneration would create noisy diffs inside the main app package
- handwritten logic and generated logic have different maintenance rules

Rule of thumb:

- `src/import_exercise_batch` is for code we own
- `libs/clients/codereviewapi` is for code generated from the backend OpenAPI spec

## UV Workspace Setup

The root project uses `uv` workspace configuration in [`pyproject.toml`](</Users/thaibao/projects/review-code-app/import-exercise-batch/pyproject.toml:1>).

Current setup:

- root package: `import-exercise-batch`
- local workspace member: `libs/clients/codereviewapi`
- dependency name used by the root app: `code_review_api_client`

This allows code in `src/` to import the generated package after syncing the environment.

Example import:

```python
import code_review_api_client
from code_review_api_client import ApiClient, Configuration
from code_review_api_client.api.problem_api import ProblemApi
```

## Recommended Usage Pattern

Application code should not spread direct generated-client calls everywhere.

Recommended layering:

1. keep generated code in `libs/clients/codereviewapi`
2. add thin wrappers or adapters in `src/import_exercise_batch`
3. let subprocess classes call those wrappers

This keeps regeneration low-risk because only wrapper code may need small updates if the API changes.

## Updating The Generated Client

When the backend OpenAPI spec changes, regenerate the client into the same folder:

```bash
npx @openapitools/openapi-generator-cli generate \
  -i /Users/thaibao/projects/review-code-app/code-review-backend/api-docs/api-docs.yaml \
  -g python \
  -o /Users/thaibao/projects/review-code-app/import-exercise-batch/libs/clients/codereviewapi
```

### Important Rules

- do not hand-edit generated files in `libs/clients/codereviewapi`
- keep custom behavior in `src/import_exercise_batch`
- review the diff after regeneration
- if the generated package metadata changes, refresh the environment

### Do You Need To Run `uv` Again

Usually:

- if only generated source files changed and the package path stays the same, no `uv add` is needed
- after regeneration, `uv sync` is a good safety step
- if dependency metadata changes, run `uv sync` or `uv lock`
- if the package path or package name changes, update `pyproject.toml` and the workspace config

## Current Design Decisions

- The batch job is class-based.
- `MainProcess` coordinates multiple subprocess classes.
- The model layer is separated into a `model/` package.
- The generated backend client is stored in `libs/clients/codereviewapi`.
- The root project depends on the generated client through the `uv` workspace.

## Notes

- The IDE may still show old files from `clients/codereviewapi`, but the active generated client location is now `libs/clients/codereviewapi`.
- There is still an empty `clients/` directory in the repo. It is not used by the current architecture and can be removed later if desired.
