#!/data/data/com.termux/files/usr/bin/python3
"""
AAR_CORE Master Loop — final minimal version
Matches the real signatures of event_store + orchestrator.
"""

import time
import traceback
import hashlib
from datetime import datetime, timezone
from event_store import EventStore
from orchestrator import run_cycle

def decision_id(genome_hash: str) -> str:
    return hashlib.sha256(f"{genome_hash}|{time.time_ns()}".encode()).hexdigest()[:16]

def main():
    store = EventStore("events.jsonl")

    # Bootstrap a few events if empty
    if len(store.replay()) == 0:
        for i in range(8):
            store.append({"type": "price_tick", "price": 100.0 + i})

    print("AAR_CORE Master Loop running — Ctrl+C to stop")
    batch = 0

    while True:
        batch += 1
        try:
            events = store.replay()
            result = run_cycle(events, seed=1000 + batch, n_cycles=5)

            did = decision_id(result["genome_hash"])
            ts = datetime.now(timezone.utc).isoformat()

            print(f"[{ts}] batch={batch}  id={did}")
            print(f"         genome={result['genome_hash'][:12]}  log={result['log_hash'][:12]}")

            store.append({
                "type": "batch_result",
                "decision_id": did,
                "genome_hash": result["genome_hash"],
                "log_hash": result["log_hash"],
                "batch": batch,
                "ts": ts
            })

        except Exception as e:
            print("ERROR:", e)
            traceback.print_exc()

        time.sleep(10)

if __name__ == "__main__":
    main()
