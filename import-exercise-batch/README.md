# import-exercise-batch

Python batch job that:

- truncates `tmp_import_exercises`
- fetches exercises from the LeetCode GraphQL API
- inserts data into `tmp_import_exercises`
- finds changed exercises versus `latest_import_exercises`
- calls a placeholder update API hook
- upserts data into `latest_import_exercises`

## Run

```bash
uv run import-exercise-batch
```

## Build wheel

```bash
uv build
```

