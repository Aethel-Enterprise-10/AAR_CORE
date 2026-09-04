import json
from orchestrator import run_cycle
from event_store import EventStore

def main():
    es = EventStore("verify_events.jsonl")
    es.clear()
    for i in range(20):
        es.append({"type": "price_tick", "price": 100 + i * 0.5})
    events = es.replay()

    configs = [
        ("full_config",        dict(safety="on",  trust_mode="on")),
        ("safety_off",         dict(safety="off", trust_mode="on")),
        ("dummy_trust",        dict(safety="on",  trust_mode="off")),
    ]

    results = {}
    for name, kwargs in configs:
        r = run_cycle(events, seed=42, **kwargs)
        results[name] = r["log_hash"]

    determinism_check = (
        run_cycle(events, seed=42, safety="on", trust_mode="on")["log_hash"]
        == results["full_config"]
    )

    all_differ = len(set(results.values())) == len(results)

    report = []
    report.append("# VERIFICATION.md\n")
    report.append("## Hashes by configuration\n")
    for name, h in results.items():
        report.append(f"- **{name}**: `{h}`")
    report.append(f"\n## All three hashes differ: {all_differ}")
    report.append(f"## Determinism (same config, same seed, rerun matches): {determinism_check}")
    report.append(f"\n## Compliance statement")
    if all_differ and determinism_check:
        report.append("This configuration satisfies the AAR compliance condition as defined "
                       "in this curriculum: hashes diverge across architectural configurations "
                       "and are reproducible under identical seed/config.")
    else:
        report.append("FAILED: does not satisfy the compliance condition. Check which "
                       "config pair collided or which rerun diverged.")

    out = "\n".join(report)
    with open("VERIFICATION.md", "w") as f:
        f.write(out)
    print(out)
    es.clear()

if __name__ == "__main__":
    main()
