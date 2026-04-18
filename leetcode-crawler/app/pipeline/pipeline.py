from app.crawler.leetcode_client import LeetCodeClient
from app.parser.problem_parser import parse_problem
from app.db.connection import get_connection
from app.db.repository import insert_problem, get_existing_ids
from app.utils.retry import retry
from app.config.settings import BATCH_SIZE

def run_pipeline(limit=50):
    client = LeetCodeClient()
    conn = get_connection()
    cur = conn.cursor()

    problems = client.get_problems(limit=limit)
    existing_ids = get_existing_ids(cur)

    for i, (_, row) in enumerate(problems.iterrows()):
        slug = row["titleSlug"]
        qid = int(row["QID"])

        try:
            if qid in existing_ids:
                print("Skip (exists):", slug)
                continue

            detail = retry(lambda: client.get_problem_detail(slug))
            parsed = parse_problem(detail["content"])

            data = {
                "question_id": detail["QID"],
                "title": detail["title"],
                "title_slug": detail["titleSlug"],
                "difficulty": detail["difficulty"],
                "content": parsed["content"],
                "html": detail["content"],
                "constraints": parsed["constraints"],
                "examples": parsed["examples"],
                "hints": detail["hints"],
                "topics": detail["topics"],
                "similar": detail["similar"],
                "is_paid": detail["is_paid"],
                "code": detail["code"]
            }

            insert_problem(cur, data)

            if i % BATCH_SIZE == 0:
                conn.commit()

            print("Saved:", detail["title"])

        except Exception as e:
            conn.rollback()
            print("Error:", slug, e)

    conn.commit()
    cur.close()
    conn.close()
