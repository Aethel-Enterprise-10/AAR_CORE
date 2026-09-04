import sqlite3
from real_data_loader import find_db

db = find_db()
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM action_history")
ah_total = cur.fetchone()[0]
print(f"action_history total rows: {ah_total}")

cur.execute("SELECT COUNT(*) FROM action_history WHERE dna_key IS NOT NULL AND pnl IS NOT NULL AND closed_time IS NOT NULL")
ah_usable = cur.fetchone()[0]
print(f"action_history rows with dna_key+pnl+closed_time all present: {ah_usable}")

# try the join at increasing time tolerance to see what actually matches
for tol in (5, 30, 60, 300):
    cur.execute(f"""
        SELECT COUNT(*) FROM action_history ah
        WHERE EXISTS (
            SELECT 1 FROM outcomes o
            WHERE o.dna_key = ah.dna_key
            AND ABS(o.pnl - ah.pnl) < 0.01
            AND ABS(o.timestamp - ah.closed_time) < {tol}
        )
    """)
    n = cur.fetchone()[0]
    print(f"action_history rows matchable to an outcomes row (tol={tol}s): {n}")

cur.execute("SELECT id, dna_key, closed_time, pnl, result FROM action_history WHERE dna_key IS NOT NULL LIMIT 5")
print("\nsample action_history rows:")
for r in cur.fetchall():
    print(dict(r))

conn.close()
