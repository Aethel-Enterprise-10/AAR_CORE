import sqlite3
from real_data_loader import find_db

db = find_db()
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT COUNT(*), COUNT(decision_id) FROM outcomes")
total, has_id = cur.fetchone()
print(f"outcomes: {has_id}/{total} rows have non-NULL decision_id")

cur.execute("SELECT COUNT(*), COUNT(decision_id) FROM decision_explanations")
total2, has_id2 = cur.fetchone()
print(f"decision_explanations: {has_id2}/{total2} rows have non-NULL decision_id")

cur.execute("SELECT decision_id FROM decision_explanations WHERE decision_id IS NOT NULL LIMIT 3")
sample = cur.fetchall()
print(f"sample real decision_ids (if any): {sample}")

cur.execute("SELECT id, loop_id, canonical_id, dna_key, decision FROM action_history LIMIT 3")
print(f"action_history sample: {cur.fetchall()}")

conn.close()
