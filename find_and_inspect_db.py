import sqlite3, os, subprocess, sys

def find_db(filename="patterns_v2.db"):
    """Searches common locations plus a filesystem find, so this never
    silently opens/creates an empty file at a wrong guessed path again."""
    candidates = [
        os.path.expanduser(f"~/{filename}"),
        os.path.expanduser(f"~/systems/shogun/{filename}"),
        os.path.expanduser(f"~/SHOGUN_OS/{filename}"),
        os.path.expanduser(f"~/shogun/{filename}"),
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.getsize(c) > 0:
            return c
    try:
        result = subprocess.run(
            ["find", os.path.expanduser("~"), "-name", filename, "-size", "+0"],
            capture_output=True, text=True, timeout=30
        )
        found = [l for l in result.stdout.strip().split("\n") if l]
        if found:
            return found[0]
    except Exception as e:
        print(f"find failed: {e}")
    return None

def inspect(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"DB: {db_path} ({os.path.getsize(db_path)} bytes)")
    print(f"tables: {tables}\n")
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in cur.fetchall()]
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        print(f"{t} ({n} rows): {cols}")
    conn.close()

if __name__ == "__main__":
    db = find_db()
    if db is None:
        print("patterns_v2.db not found under home directory (or all matches were empty/0 bytes).")
        print("Run manually: find ~ -iname '*.db' -size +0 2>/dev/null")
        sys.exit(1)
    inspect(db)
