
import json
from typing import List, Optional, Dict, Any
from numpy.distutils import log

from app.parser.problem_parser import extract_description


def _parse_constraints(value):
    """Parse constraints from database"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return [value]
    return []


def _parse_examples(value):
    """Parse examples from database"""
    if value is None:
        print("EXAMPLES VALUE IS NONE")
        return {}
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, dict):
        print("EXAMPLES IS A DICT")
        print("TYPE:", type(value))
        print("VALUE:", value)
        return value
    if isinstance(value, str):
        try:
            print("EXAMPLES IS A STRING")
            print("TYPE:", type(value))
            print("VALUE:", value)
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    print("EXAMPLES IS OF UNEXPECTED TYPE")
    return {}


def _normalize_string_list(value):
    """Normalize scalar/list/json-string values into a list of strings for text[] columns."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                normalized = []
                for item in parsed:
                    if isinstance(item, dict):
                        normalized.append(
                            item.get("title")
                            or item.get("titleSlug")
                            or json.dumps(item, ensure_ascii=False)
                        )
                    else:
                        normalized.append(str(item))
                return normalized
        except json.JSONDecodeError:
            pass
        return [value]
    return [str(value)]


def _normalize_int_list(value):
    """Normalize scalar/list/json-string values into a list of ints for integer[] columns."""
    if value is None:
        return []

    def _to_int_or_none(item):
        if isinstance(item, bool):
            return None
        if isinstance(item, int):
            return item
        if isinstance(item, float) and item.is_integer():
            return int(item)
        if isinstance(item, str):
            stripped = item.strip()
            if stripped.isdigit():
                return int(stripped)
            return None
        if isinstance(item, dict):
            for key in ("questionFrontendId", "question_id", "QID", "id"):
                candidate = item.get(key)
                normalized = _to_int_or_none(candidate)
                if normalized is not None:
                    return normalized
            return None
        return None

    raw_items = value
    if isinstance(value, str):
        try:
            raw_items = json.loads(value)
        except json.JSONDecodeError:
            raw_items = [value]

    if not isinstance(raw_items, list):
        raw_items = [raw_items]

    normalized = []
    for item in raw_items:
        parsed = _to_int_or_none(item)
        if parsed is not None:
            normalized.append(parsed)

    return normalized


def insert_problem(cur, data):
    cur.execute("""
        INSERT INTO problems (
            question_id, title, title_slug, difficulty,
            content, html_content, constraints, examples,
            hints, topics, similar_questions,
            is_paid_only, code_snippet
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s)
        ON CONFLICT (question_id) DO NOTHING;
    """, (
        data["question_id"],
        data["title"],
        data["title_slug"],
        data["difficulty"],
        data["content"],
        data["html"],
        json.dumps(data.get("constraints", [])),     # constraints as JSONB array
        json.dumps(data.get("examples", {})),        # examples as JSONB object
        _normalize_string_list(data.get("hints")),
        _normalize_string_list(data.get("topics")),
        _normalize_int_list(data.get("similar")),
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


def get_problem_by_id(cur, question_id: int) -> Optional[Dict[str, Any]]:
    """Get a single problem by question ID"""
    cur.execute("""
        SELECT title, difficulty, content, constraints, examples, code_snippet
        FROM problems
        WHERE question_id = %s
    """, (question_id,))
    
    row = cur.fetchone()
    if not row:
        return None
    
    return {
        "title": row[0],
        "difficulty": row[1],
        "content": row[2],
        "constraints": _parse_constraints(row[3]),
        "examples": _parse_examples(row[4]),
        "code_snippet": row[5]
    }


def get_problem_by_title_slug(cur, title_slug: str) -> Optional[Dict[str, Any]]:
    """Get a single problem by title slug"""
    cur.execute("""
        SELECT title, difficulty, content, constraints, examples, code_snippet
        FROM problems
        WHERE title_slug = %s
    """, (title_slug,))
    
    row = cur.fetchone()
    if not row:
        return None
    
    return {
        "title": row[0],
        "difficulty": row[1],
        "content": row[2],
        "constraints": _parse_constraints(row[3]),
        "examples": _parse_examples(row[4]),
        "code_snippet": row[5]
    }


def get_all_problems(cur, page: int = 1, limit: int = 10) -> tuple[List[Dict[str, Any]], int]:
    """Get paginated list of all problems with total count"""
    # Get total count
    cur.execute("SELECT COUNT(*) FROM problems")
    total = cur.fetchone()[0]
    
    # Get paginated data
    offset = (page - 1) * limit
    cur.execute("""
        SELECT title, difficulty, content, constraints, examples, code_snippet
        FROM problems
        ORDER BY question_id ASC
        LIMIT %s OFFSET %s
    """, (limit, offset))
    
    rows = cur.fetchall()
    problems = []

    print(f"Fetched {len(rows)} rows from database for page {page} with limit {limit}")
    
    for row in rows:
        print(_parse_examples(row[4]))
        problems.append({
            "title": row[0],
            "difficulty": row[1],
            "content": extract_description(row[2]),
            "constraints": _parse_constraints(row[3]),
            "examples": _parse_examples(row[4]),
            "code_snippet": row[5]
        })
    
    return problems, total


def get_problems_by_difficulty(cur, difficulty: str, page: int = 1, limit: int = 10) -> tuple[List[Dict[str, Any]], int]:
    """Get problems filtered by difficulty"""
    # Get total count
    cur.execute("SELECT COUNT(*) FROM problems WHERE difficulty = %s", (difficulty,))
    total = cur.fetchone()[0]
    
    # Get paginated data
    offset = (page - 1) * limit
    cur.execute("""
        SELECT title, difficulty, content, constraints, examples, code_snippet
        FROM problems
        WHERE difficulty = %s
        ORDER BY question_id ASC
        LIMIT %s OFFSET %s
    """, (difficulty, limit, offset))
    
    rows = cur.fetchall()
    problems = []
    
    for row in rows:
        problems.append({
            "title": row[0],
            "difficulty": row[1],
            "content": row[2],
            "constraints": _parse_constraints(row[3]),
            "examples": _parse_examples(row[4]),
            "code_snippet": row[5]
        })
    
    return problems, total
