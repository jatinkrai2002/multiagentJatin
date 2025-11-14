"""
Jatin K Rai


Persistent Memory: 
    Each agent saves its state in a JSON file (collector_memory.json, etc.). This persists across runs.
    Memory corruption when JSON file was interrupted.


•	Routing Policy: 
    Orchestrator maps task types (collect, analyze, report) to specific agents.
    Added error handling with fallback to empty memory.

•	Sequential Workflow: 
    Tasks flow from Collector → Analyzer → Reporter, with outputs passed step-by-step.
    Sequential dependencies (Analyzer needs Collector’s output) and Orchestrator enforces pipeline order and passes intermediate results.

•	Debugging: 
    Logging tracks agent activity, routing decisions, and memory issues.
    Debugging agent interactions and Introduced logging with timestamps and task identifiers.

•	Memory Management: 
    Agents prune or overwrite memory per task to avoid uncontrolled growth.
    Memory bloat and Agents overwrite task entries or prune old tasks.


"""
import json
import logging
from typing import Dict, Any

"""
Multi-agent orchestration

Persistent memory per agent

Routing policies

Debugging/logging

Memory management and sequential workflows

"""

# --- Setup logging for debugging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Base Agent Class ---
class Agent:
    def __init__(self, name: str, memory_file: str):
        self.name = name
        self.memory_file = memory_file
        self.memory: Dict[str, Any] = self.load_memory()

    def load_memory(self) -> Dict[str, Any]:
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logging.warning(f"{self.name}: Memory file corrupted, starting fresh.")
            return {}

    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def process(self, task: str, data: Any) -> str:
        """Override in subclasses"""
        raise NotImplementedError


# --- Specific Agents ---
class CollectorAgent(Agent):
    def process(self, task: str, data: Any) -> str:
        logging.info(f"{self.name} collecting data for task: {task}")
        result = f"Collected raw data: {data}"
        self.memory[task] = result
        self.save_memory()
        return result


class AnalyzerAgent(Agent):
    def process(self, task: str, data: Any) -> str:
        logging.info(f"{self.name} analyzing data for task: {task}")
        result = f"Analyzed summary of: {data}"
        self.memory[task] = result
        self.save_memory()
        return result


class ReporterAgent(Agent):
    def process(self, task: str, data: Any) -> str:
        logging.info(f"{self.name} reporting results for task: {task}")
        result = f"Final report generated: {data}"
        self.memory[task] = result
        self.save_memory()
        return result

# --- Orchestrator ---
class Orchestrator:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.routing_policy: Dict[str, str] = {}

    def register_agent(self, agent: Agent, task_type: str):
        self.agents[agent.name] = agent
        self.routing_policy[task_type] = agent.name

    def route(self, task_type: str, task: str, data: Any) -> str:
        if task_type not in self.routing_policy:
            raise ValueError(f"No agent registered for task type: {task_type}")
        agent_name = self.routing_policy[task_type]
        agent = self.agents[agent_name]
        logging.info(f"Routing task '{task}' to agent '{agent_name}'")
        return agent.process(task, data)

# --- Workflow to complete ---
if __name__ == "__main__":
    # Initialize agents with persistent memory files
    collector = CollectorAgent("Collector", "collector_memory.json")
    analyzer = AnalyzerAgent("Analyzer", "analyzer_memory.json")
    reporter = ReporterAgent("Reporter", "reporter_memory.json")

    # Setup orchestrator
    orch = Orchestrator()
    orch.register_agent(collector, "collect")
    orch.register_agent(analyzer, "analyze")
    orch.register_agent(reporter, "report")

    # Sequential workflow
    raw_data = orch.route("collect", "task1", "User input text")
    analyzed = orch.route("analyze", "task1", raw_data)
    final_report = orch.route("report", "task1", analyzed)

    print("\n--- Workflow Results ---")
    print(final_report)
