def build_world_state(events: list, up_to_index: int = None) -> dict:
    """Pure function: same events -> same output, every time.
    No datetime.now(), no random, no external calls allowed here."""
    slice_ = events if up_to_index is None else events[:up_to_index]
    prices = [e["price"] for e in slice_ if e.get("type") == "price_tick"]
    if not prices:
        return {"last_price": None, "volatility": 0.0, "n": 0}
    last = prices[-1]
    if len(prices) > 1:
        diffs = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        vol = sum(diffs) / len(diffs)
    else:
        vol = 0.0
    return {"last_price": last, "volatility": round(vol, 4), "n": len(prices)}

if __name__ == "__main__":
    events = [{"type": "price_tick", "price": 100 + i} for i in range(10)]
    s1 = build_world_state(events)
    s2 = build_world_state(events)
    assert s1 == s2
    print("OK: world model is deterministic on repeated calls:", s1)
