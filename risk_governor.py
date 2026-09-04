def compute_allocation(trust: float, variance: float, max_allocation: float = 0.25):
    confidence_factor = max(0.0, 1.0 - min(1.0, variance * 5))
    raw = trust * confidence_factor
    allocation = min(max_allocation, raw)
    reason = []
    if raw > max_allocation: reason.append(f"clamped_by_max_allocation({max_allocation})")
    if confidence_factor < 0.5: reason.append(f"low_confidence(var={variance:.5f})")
    if not reason: reason.append("within_bounds")
    return {"allocation": round(allocation,4), "reason": reason}

def safety_layer(decision: dict, consecutive_losses: int, hard_ceiling: float = 0.15, cooldown_after: int = 3):
    decision = dict(decision)
    if consecutive_losses >= cooldown_after:
        decision["allocation"] = 0.0
        decision["reason"].append(f"safety_cooldown(losses={consecutive_losses})")
        return decision
    if decision["allocation"] > hard_ceiling:
        decision["allocation"] = hard_ceiling
        decision["reason"].append(f"safety_hard_ceiling({hard_ceiling})")
    return decision
