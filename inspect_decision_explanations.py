import sqlite3, re
from real_data_loader import find_db

db = find_db()
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# FIXED: original pattern [\w.]+ excluded hyphens, so real keys like
# "20K-25K|85-90|Night" were misclassified as noise. Verified against
# synthetic data before running here -- [\w.-]+ correctly matches now.
zone_pattern = re.compile(r'^[\w.-]+\|[\w.-]+\|\w+$')

cur.execute("SELECT dna_key, decision_id, timestamp FROM decision_explanations")
rows = cur.fetchall()

real_zone_rows = [r for r in rows if r["dna_key"] and zone_pattern.match(r["dna_key"])]
noise_rows = [r for r in rows if r["dna_key"] and not zone_pattern.match(r["dna_key"])]

print(f"total decision_explanations rows: {len(rows)}")
print(f"rows with real zone-pattern dna_key: {len(real_zone_rows)}")
print(f"rows that look like chat/noise: {len(noise_rows)}")

if real_zone_rows:
    print("\nsample real zone-pattern rows:")
    for r in real_zone_rows[:5]:
        print(dict(r))

real_keys = set(r["dna_key"] for r in real_zone_rows)
cur.execute("SELECT DISTINCT dna_key FROM outcomes")
outcome_keys = set(r["dna_key"] for r in cur.fetchall())
overlap = real_keys & outcome_keys
print(f"\nreal decision_explanations dna_keys that also appear in outcomes: {len(overlap)} of {len(real_keys)}")

cur.execute("SELECT MIN(timestamp) as lo, MAX(timestamp) as hi FROM outcomes")
r = cur.fetchone()
print(f"\noutcomes timestamp range: {r['lo']} to {r['hi']}")

cur.execute("SELECT MIN(timestamp) as lo, MAX(timestamp) as hi FROM decision_explanations WHERE dna_key IS NOT NULL")
r = cur.fetchone()
print(f"decision_explanations timestamp range: {r['lo']} to {r['hi']}")

conn.close()
