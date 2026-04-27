# import-exercise-batch

Python batch job that:

- truncates `tmp_import_exercises`
- fetches exercises from the LeetCode GraphQL API
- inserts data into `tmp_import_exercises`
- finds changed exercises versus `latest_import_exercises`
- calls the code review import subprocess
- calls the review agent knowledge graph import subprocess
- upserts data into `latest_import_exercises`

## Run

```bash
uv run import-exercise-batch
```

Set `CODEREVIEWAI_API_MAX_WORKERS` to control the CodeReviewAI thread pool size used by both
`import_exercise` and `import_topic` batches. The default is `8`.

## Build wheel

```bash
uv build
```

## Postgres Schema

`tmp_import_exercises`

```sql
CREATE TABLE tmp_import_exercises (
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    topic_tag_slugs TEXT NOT NULL,
    similar_question_slugs TEXT NOT NULL
);
```

`latest_import_exercises`

```sql
CREATE TABLE latest_import_exercises (
    exercise_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    topic_tag_slugs TEXT NOT NULL,
    similar_question_slugs TEXT NOT NULL
);
```

If you use `gen_random_uuid()`, make sure `pgcrypto` is enabled:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```
