# shared_protocol.py

"""
Jatin K Rai

"""
import json
import logging

ALLOWED_TASK_TYPES = {"collect", "analyze", "report"}
REQUIRED_FIELDS = {"task_id", "task_type", "data", "auth_token"}

def encode_message(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")

def decode_message(line: bytes) -> dict:
    try:
        obj = json.loads(line.decode("utf-8").strip())
        return obj
    except Exception as e:
        logging.error(f"Protocol decode error: {e}")
        return {"error": "decode_error", "detail": str(e)}

def validate_request(req: dict, expected_task_types=None) -> tuple[bool, str]:
    if not isinstance(req, dict):
        return False, "invalid_format"
    missing = REQUIRED_FIELDS - set(req.keys())
    if missing:
        return False, f"missing_fields:{','.join(sorted(missing))}"
    if expected_task_types is None:
        expected_task_types = ALLOWED_TASK_TYPES
    if req["task_type"] not in expected_task_types:
        return False, "invalid_task_type"
    if not isinstance(req["task_id"], str) or not req["task_id"]:
        return False, "invalid_task_id"
    if not isinstance(req["data"], (str, dict, list)):
        return False, "invalid_data"
    return True, "ok"

def make_response(task_id: str, status: str, result=None, error=None) -> dict:
    return {
        "task_id": task_id,
        "status": status,
        "result": result,
        "error": error
    }
