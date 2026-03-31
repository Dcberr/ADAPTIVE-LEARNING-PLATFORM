import json

def insert_problem(cur, data):
    cur.execute("""
        INSERT INTO problems (
            question_id, title, title_slug, difficulty,
            content, html_content, constraints, examples,
            hints, topics, similar_questions,
            is_paid_only, code_snippet
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (question_id) DO NOTHING;
    """, (
        data["question_id"],
        data["title"],
        data["title_slug"],
        data["difficulty"],
        data["content"],
        data["html"],
        data["constraints"],              # list[str]
        json.dumps(data["examples"]),     # JSONB
        data["hints"],
        data["topics"],
        data["similar"],
        data["is_paid"],
        data["code"]
    ))

def exists_problem(cur, question_id):
    cur.execute(
        "SELECT 1 FROM problems WHERE question_id = %s LIMIT 1",
        (question_id,)
    )
    return cur.fetchone() is not None

def get_existing_ids(cur):
    cur.execute("SELECT question_id FROM problems")
    return set(row[0] for row in cur.fetchall())