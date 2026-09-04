import hashlib, json, random
from event_store import EventStore
from trust_engine import TrustEngine
from world_model import build_world_state
from risk_governor import compute_allocation, safety_layer
from genome import genome_hash, DEFAULT_GENOME

def run_cycle(events: list, seed: int, mode="full", safety="on", trust_mode="on",
              n_cycles=10):
    rng = random.Random(seed)
    te = TrustEngine(decay=0.88) if trust_mode == "on" else None
    consecutive_losses = 0
    decision_log = []

    for cycle in range(n_cycles):
        state = build_world_state(events)
        outcome = rng.choice(["win", "win", "loss"])  # synthetic outcome for demo
        if te is not None:
            trust, var = te.update(outcome)
        else:
            trust, var = 0.5, 0.01  # dummy trust: ignores real outcomes

        decision = compute_allocation(trust, var)
        if safety == "on":
            decision = safety_layer(decision, consecutive_losses)

        consecutive_losses = consecutive_losses + 1 if outcome == "loss" else 0
        decision["cycle"] = cycle
        decision["outcome"] = outcome
        decision["world_state"] = state
        decision_log.append(decision)

    genome = dict(DEFAULT_GENOME)
    genome["safety_layer"] = safety
    genome["trust_engine"] = trust_mode
    g_hash = genome_hash(genome)

    log_str = json.dumps(decision_log, sort_keys=True)
    log_hash = hashlib.sha256(log_str.encode()).hexdigest()

    return {"decision_log": decision_log, "genome_hash": g_hash, "log_hash": log_hash}

if __name__ == "__main__":
    es = EventStore("demo_events.jsonl")
    es.clear()
    for i in range(20):
        es.append({"type": "price_tick", "price": 100 + i * 0.5})
    events = es.replay()

    r1 = run_cycle(events, seed=42, mode="full", safety="on", trust_mode="on")
    r2 = run_cycle(events, seed=42, mode="full", safety="on", trust_mode="on")
    r3 = run_cycle(events, seed=42, mode="full", safety="off", trust_mode="on")
    r4 = run_cycle(events, seed=42, mode="full", safety="on", trust_mode="off")

    print("determinism check (r1 == r2):", r1["log_hash"] == r2["log_hash"])
    print("safety-off changes hash:", r1["log_hash"] != r3["log_hash"])
    print("dummy-trust changes hash:", r1["log_hash"] != r4["log_hash"])
    print("genome hashes differ across configs:",
          len({r1["genome_hash"], r3["genome_hash"], r4["genome_hash"]}) == 3)

    # substantive check, not just hash: did safety actually change an allocation?
    diffs = [i for i,(a,b) in enumerate(zip(r1["decision_log"], r3["decision_log"]))
             if a["allocation"] != b["allocation"]]
    print(f"decisions where safety changed the actual allocation: {len(diffs)} of 10")
    es.clear()
