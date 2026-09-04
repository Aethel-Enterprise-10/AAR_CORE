import json, os, time

class EventStore:
    def __init__(self, path="events.jsonl"):
        self.path = path

    def append(self, event: dict):
        event = dict(event)
        event.setdefault("ts", time.time())
        with open(self.path, "a") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")

    def replay(self, from_index=0):
        if not os.path.exists(self.path):
            return []
        with open(self.path) as f:
            lines = f.readlines()
        return [json.loads(l) for l in lines[from_index:]]

    def clear(self):
        if os.path.exists(self.path):
            os.remove(self.path)

if __name__ == "__main__":
    es = EventStore("test_events.jsonl")
    es.clear()
    for i in range(5):
        es.append({"type": "price_tick", "price": 100 + i, "seq": i})
    events = es.replay()
    print(f"replayed {len(events)} events")
    assert len(events) == 5
    print("OK: event store append/replay works")
    es.clear()
