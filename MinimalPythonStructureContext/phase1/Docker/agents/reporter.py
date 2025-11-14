# agents/reporter.py

"""
 Jatin K Rai


"""
from agent_server import handle_task, AGENT_NAME
AGENT_NAME = "reporter"

def handle_task(task_type, data, memory):
    if task_type != "report":
        return f"reporter: unsupported {task_type}"
    # format structured report
    return f"REPORT:\n- Content: {data}\n- Status: ready"

