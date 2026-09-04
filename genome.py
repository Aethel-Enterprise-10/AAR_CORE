import json, hashlib

def genome_hash(config: dict) -> str:
    """Canonical serialization -> SHA-256. sort_keys is mandatory:
    without it, identical configs with different dict insertion order
    produce false hash mismatches."""
    canonical = json.dumps(config, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()

DEFAULT_GENOME = {
    "trust_engine": "on",
    "safety_layer": "on",
    "world_model": "on",
    "risk_governor": "on",
    "decay": 0.88,
    "version": "AAR-CORE-0.1",
}

if __name__ == "__main__":
    g1 = dict(DEFAULT_GENOME)
    g2 = dict(DEFAULT_GENOME); g2["trust_engine"] = "off"
    print("full:", genome_hash(g1)[:16])
    print("trust-off:", genome_hash(g2)[:16])
    assert genome_hash(g1) != genome_hash(g2)
    print("OK: genome hash changes when trust_engine toggled")
