"""
Jatin K Rai
"""

# agents/analyzer.py
from agent_server import handle_task, AGENT_NAME
AGENT_NAME = "analyzer"

def handle_task(task_type, data, memory):
    if task_type != "analyze":
        return f"analyzer: unsupported {task_type}"
    # example: basic summarization/counts
    text = str(data)
    length = len(text)
    return {"summary": text[:100], "length": length}
