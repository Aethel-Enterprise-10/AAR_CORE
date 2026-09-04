#!/data/data/com.termux/files/usr/bin/python3
import hashlib
import time
from event_store import EventStore
from orchestrator import run_cycle

def make_structured_events(n=30):
    events = []
    price = 100.0
    for i in range(n):
        price += 0.15 + (0.4 if i % 5 == 0 else -0.1)
        events.append({
            "type": "price_tick",
            "price": round(price, 4),
            "seq": i,
            "regime": "uptrend" if price > 102 else "neutral"
        })
    return events

def decision_id(genome_hash):
    return hashlib.sha256(f"{genome_hash}|{time.time_ns()}".encode()).hexdigest()[:16]

def main():
    print("=== AAR_CORE Structured Data Test ===\n")
    store = EventStore("structured_test.jsonl")
    store.clear()
    structured = make_structured_events(30)
    for e in structured:
        store.append(e)
    events = store.replay()
    print(f"Loaded {len(events)} structured events")
    print(f"Price range: {events[0 -1]['price']}\n")
    r1 = run_cycle(events, seed=77, n_cycles=5)
    id1 = decision_id(r1 )
    r2 = run_cycle(events, seed=77, n_cycles=5)
    id2 = decision_id(r2 )
    print(f"Run 1  genome={r1 [:16 :16]}  id={id1}")
    print(f"Run 2  genome={r2 [:16]}  log={r2 [:16 "genome_hash" "log_hash"]
    print("=== VERIFICATION ===")
    print(f"Genome hash match : {genome_match}")
    print(f"Log hash match    : {log_match}")
    if genome_match and log_match:
        print("\nPASS - structured data produces identical verifiable results")
    else:
        print("\nFAIL - hashes diverged")
    store.append({
        "type": "verification_result",
        "genome_match": genome_match,
        "log_match": log_match,
        "genome_hash": r1 ,
        "log_hash": r1 })

if __name__ == "__main__":
    main()
