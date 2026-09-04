import sqlite3
from real_data_loader import find_db

db = find_db()
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Confirm dna_key actually overlaps between the two tables --
# if it doesn't, timestamp-nearest-match is the wrong join key.
cur.execute("SELECT DISTINCT dna_key FROM outcomes LIMIT 5")
o_keys = [r["dna_key"] for r in cur.fetchall()]
print("sample outcomes.dna_key:", o_keys)

cur.execute("SELECT DISTINCT dna_key FROM decision_explanations LIMIT 5")
d_keys = [r["dna_key"] for r in cur.fetchall()]
print("sample decision_explanations.dna_key:", d_keys)

cur.execute("""
    SELECT COUNT(*) FROM outcomes o
    WHERE EXISTS (
        SELECT 1 FROM decision_explanations d WHERE d.dna_key = o.dna_key
    )
""")
overlap = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM outcomes")
total = cur.fetchone()[0]
print(f"\noutcomes rows with a dna_key that exists in decision_explanations: {overlap}/{total}")

# check timestamp ranges overlap -- outcomes.timestamp looks like unix epoch,
# decision_explanations.timestamp needs checking against the same format
cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM outcomes")
print("outcomes timestamp range:", cur.fetchone())
cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM decision_explanations")
print("decision_explanations timestamp range:", cur.fetchone())

conn.close()
