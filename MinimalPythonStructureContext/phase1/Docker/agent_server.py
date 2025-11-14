"""
Jatin K Rai

"""

# agent_server.py
import socket
import logging
import json
import os
from typing import Any, Dict
from shared_protocol import decode_message, encode_message, validate_request, make_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "change-me")
MEMORY_FILE = os.environ.get("MEMORY_FILE", "/data/memory.json")
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "7000"))
AGENT_NAME = os.environ.get("AGENT_NAME", "agent")

def load_memory() -> Dict[str, Any]:
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logging.error(f"{AGENT_NAME}: Memory load error: {e}")
        return {}

def save_memory(mem: Dict[str, Any]):
    try:
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, "w") as f:
            json.dump(mem, f, indent=2)
    except Exception as e:
        logging.error(f"{AGENT_NAME}: Memory save error: {e}")

def handle_task(task_type: str, data: Any, memory: Dict[str, Any]) -> Any:
    # Override with agent-specific logic
    return f"{AGENT_NAME} processed {task_type} -> {data}"

def start_server():
    memory = load_memory()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(64)
    logging.info(f"{AGENT_NAME} listening on {HOST}:{PORT}")

    while True:
        conn, addr = sock.accept()
        conn.settimeout(5.0)  # security: avoid hanging connections
        try:
            buffer = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                # process line-delimited messages
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    req = decode_message(line)
                    ok, reason = validate_request(req, expected_task_types={task_type for task_type in [req.get("task_type")] if task_type})
                    if not ok:
                        resp = make_response(req.get("task_id", ""), "error", error=reason)
                        conn.sendall(encode_message(resp))
                        continue
                    if req["auth_token"] != AUTH_TOKEN:
                        resp = make_response(req["task_id"], "error", error="unauthorized")
                        conn.sendall(encode_message(resp))
                        continue
                    try:
                        result = handle_task(req["task_type"], req["data"], memory)
                        # persist memory per task_id
                        memory[req["task_id"]] = {
                            "task_type": req["task_type"],
                            "data": req["data"],
                            "result": result
                        }
                        save_memory(memory)
                        resp = make_response(req["task_id"], "ok", result=result)
                        conn.sendall(encode_message(resp))
                    except Exception as e:
                        logging.error(f"{AGENT_NAME} processing error: {e}")
                        resp = make_response(req["task_id"], "error", error="processing_error")
                        conn.sendall(encode_message(resp))
        except socket.timeout:
            logging.warning(f"{AGENT_NAME}: connection timeout from {addr}")
        except Exception as e:
            logging.error(f"{AGENT_NAME}: connection error {addr}: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    start_server()
