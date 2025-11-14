"""
Jatin K Rai

"""

# orchestrator.py
import socket
import time
import logging
import json
import os
from typing import Dict, Any
from shared_protocol import encode_message, decode_message, make_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "change-me")
ROUTES = {
    "collect": ("collector", 7001),
    "analyze": ("analyzer", 7002),
    "report": ("reporter", 7003)
}
TASK_LOG: Dict[str, Dict[str, Any]] = {}

def send_request(host: str, port: int, payload: Dict[str, Any], retries: int = 3, backoff: float = 0.5) -> Dict[str, Any]:
    attempt = 0
    while attempt < retries:
        try:
            with socket.create_connection((host, port), timeout=3.0) as s:
                s.sendall(encode_message(payload))
                data = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if b"\n" in data:
                        line, _ = data.split(b"\n", 1)
                        resp = decode_message(line)
                        return resp
        except Exception as e:
            logging.error(f"orchestrator send error to {host}:{port}: {e}")
            time.sleep(backoff * (2 ** attempt))
            attempt += 1
    return {"task_id": payload.get("task_id", ""), "status": "error", "error": "network_failure"}

def route(task_id: str, task_type: str, data: Any) -> Dict[str, Any]:
    if task_type not in ROUTES:
        return make_response(task_id, "error", error="route_not_found")
    host, port = ROUTES[task_type]
    payload = {"task_id": task_id, "task_type": task_type, "data": data, "auth_token": AUTH_TOKEN}
    resp = send_request(host, port, payload)
    TASK_LOG[task_id] = {"step": task_type, "response": resp}
    return resp

def dashboard():
    print("\n=== Monitoring Dashboard ===")
    for tid, info in TASK_LOG.items():
        status = info["response"].get("status")
        step = info["step"]
        print(f"Task {tid} | Step: {step} | Status: {status}")
    print("============================\n")

def run_pipeline(task_id: str, user_text: str) -> Dict[str, Any]:
    r1 = route(task_id, "collect", user_text)
    if r1.get("status") != "ok":
        return r1
    r2 = route(task_id, "analyze", r1.get("result"))
    if r2.get("status") != "ok":
        return r2
    r3 = route(task_id, "report", r2.get("result"))
    dashboard()
    return r3

if __name__ == "__main__":
    final = run_pipeline("task-001", "   Hello Chennai! This is a sample input to process.   ")
    print("\n--- Final Output ---")
    print(json.dumps(final, indent=2))
