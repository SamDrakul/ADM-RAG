import json, os, time
AUDIT_DIR = os.getenv("AUDIT_DIR", "audit")

def write_audit(run_id: str, payload: dict):
    os.makedirs(AUDIT_DIR, exist_ok=True)
    path = os.path.join(AUDIT_DIR, f"{run_id}.json")
    payload["_ts"] = time.time()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return {"ok": True, "audit": path}
