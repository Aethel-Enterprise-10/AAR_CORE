import hashlib, json
from trust_engine import TrustEngine
from risk_governor import compute_allocation, safety_layer
from genome import genome_hash, DEFAULT_GENOME
from real_data_loader import find_db, load_real_outcomes

def run_cycle_real(outcome_rows, safety="on", trust_mode="on", decay=0.88):
    te = TrustEngine(decay=decay) if trust_mode == "on" else None
    consecutive_losses = 0
    decision_log = []

    for row in outcome_rows:
        outcome = row["outcome"]
        if te is not None:
            trust, var = te.update(outcome)
        else:
            trust, var = 0.5, 0.01

        decision = compute_allocation(trust, var)
        if safety == "on":
            decision = safety_layer(decision, consecutive_losses)

        consecutive_losses = consecutive_losses + 1 if outcome == "loss" else 0
        decision["outcome"] = outcome
        decision["canonical_id"] = row["canonical_id"]
        decision["decision_id"] = row["decision_id"]
        decision_log.append(decision)

    genome = dict(DEFAULT_GENOME)
    genome["safety_layer"] = safety
    genome["trust_engine"] = trust_mode
    g_hash = genome_hash(genome)
    log_hash = hashlib.sha256(json.dumps(decision_log, sort_keys=True, default=str).encode()).hexdigest()
    return {"decision_log": decision_log, "genome_hash": g_hash, "log_hash": log_hash}

if __name__ == "__main__":
    db = find_db()
    data = load_real_outcomes(db, limit=500)

    r1 = run_cycle_real(data, safety="on", trust_mode="on")
    r2 = run_cycle_real(data, safety="on", trust_mode="on")
    r3 = run_cycle_real(data, safety="off", trust_mode="on")
    r4 = run_cycle_real(data, safety="on", trust_mode="off")

    print(f"ran {len(data)} real outcome rows through the pipeline\n")
    print("determinism (r1==r2):", r1["log_hash"] == r2["log_hash"])
    print("safety-off changes hash:", r1["log_hash"] != r3["log_hash"])
    print("dummy-trust changes hash:", r1["log_hash"] != r4["log_hash"])

    diffs = [i for i,(a,b) in enumerate(zip(r1["decision_log"], r3["decision_log"]))
             if a["allocation"] != b["allocation"]]
    print(f"decisions where safety changed real allocation: {len(diffs)} of {len(data)}")

    final_trust = r1["decision_log"][-1]
    print(f"\nfinal trust-driven allocation on real data: {final_trust['allocation']}, reason: {final_trust['reason']}")
