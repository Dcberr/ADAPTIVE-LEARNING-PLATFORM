"""
Script to clean and re-crawl all problems with improved parser
Run: python -m scripts.clean_and_recrawl
"""

from app.db.connection import get_connection


def clean_problems_table():
    """Delete all problems to allow re-crawling with new parser"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get count before deleting
        cur.execute("SELECT COUNT(*) FROM problems")
        count = cur.fetchone()[0]
        print(f"Found {count} problems in database")
        
        if count > 0:
            confirm = input(f"\nDelete all {count} problems? (yes/no): ")
            if confirm.lower() == "yes":
                cur.execute("DELETE FROM problems")
                conn.commit()
                print(f"✅ Deleted {count} problems from database")
                print("\nNow run: python -m scripts.run_crawler")
            else:
                print("❌ Aborted")
        else:
            print("No problems to delete")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    clean_problems_table()
