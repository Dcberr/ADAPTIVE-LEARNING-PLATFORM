"""Debug script to check examples data in database"""
from app.db.connection import get_connection
from app.db import repository
import json


def check_examples():
    conn = get_connection()
    cur = conn.cursor()
    
    # Buscar alguns problems com seus examples
    cur.execute("""
        SELECT question_id, title, examples, pg_typeof(examples)
        FROM problems
        LIMIT 5
    """)
    
    rows = cur.fetchall()
    for row in rows:
        q_id, title, examples, pg_type = row
        print(f"\nQuestion ID: {q_id}")
        print(f"Title: {title}")
        print(f"PostgreSQL Type: {pg_type}")
        print(f"Examples Value: {repr(examples)}")
        print(f"Examples Type (Python): {type(examples)}")
        if examples:
            print(f"Examples (formatted): {json.dumps(examples, indent=2) if isinstance(examples, dict) else examples}")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    check_examples()
