import sqlite3
import sys
import os


def apply(sql_path: str, db_path: str):
    if not os.path.exists(sql_path):
        print("Migration file not found:", sql_path)
        return 2
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql)
        conn.commit()
        print("Applied migration to:", db_path)
    finally:
        conn.close()

    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    sql = argv[1]
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base, "backend", "mermelab_v2.db")
    return apply(sql, db_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
