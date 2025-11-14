"""
Jatin K Rai

"""

# agents/collector.py
from agent_server import handle_task, AGENT_NAME
AGENT_NAME = "collector"  # override the default name

def handle_task(task_type, data, memory):
    # simple sanitization
    if task_type != "collect":
        return f"collector: unsupported {task_type}"
    # pretend to normalize input
    if isinstance(data, str):
        cleaned = data.strip()
    else:
        cleaned = data
    return f"collected:{cleaned}"
