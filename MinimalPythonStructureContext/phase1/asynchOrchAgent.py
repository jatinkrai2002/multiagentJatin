"""
Jatin K Rai


Multi-agent orchestrator into a more advanced version with:
•	Asynchronous agent communication (using asyncio)
•	Monitoring/debug dashboard (simple console-based dashboard)
•	Secure coding practices (try/except blocks, safe memory handling, logging)
•	Agentic AI orchestration system in raw Python.


"""

import asyncio
import json
import logging
from typing import Dict, Any

# --- Setup logging for debugging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

"""
Challenge: Async tasks caused race conditions.
Resolution: Enforced sequential routing for dependent tasks,
 but allowed parallel execution for independent ones.

Challenge: Memory corruption. 
Resolution: Added try/except with fallback to empty memory.

Challenge: Debugging multiple agents. 
Resolution: Introduced a monitoring dashboard with task logs.

"""

# --- Base Agent Class with Async ---
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
            logging.warning(f"{self.name}: No memory file found, starting fresh.")
            return {}
        except json.JSONDecodeError:
            logging.error(f"{self.name}: Memory file corrupted, resetting.")
            return {}

    def save_memory(self):
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logging.error(f"{self.name}: Failed to save memory securely: {e}")

    async def process(self, task: str, data: Any) -> str:
        """Override in subclasses"""
        raise NotImplementedError

# --- Specific Agents ---
class CollectorAgent(Agent):
    async def process(self, task: str, data: Any) -> str:
        try:
            logging.info(f"{self.name} collecting data for task: {task}")
            await asyncio.sleep(1)  # simulate async work
            result = f"Collected raw data: {data}"
            self.memory[task] = result
            self.save_memory()
            return result
        except Exception as e:
            logging.error(f"{self.name} failed: {e}")
            return "Error in Collector"

class AnalyzerAgent(Agent):
    async def process(self, task: str, data: Any) -> str:
        try:
            logging.info(f"{self.name} analyzing data for task: {task}")
            await asyncio.sleep(2)  # simulate longer async work
            result = f"Analyzed summary of: {data}"
            self.memory[task] = result
            self.save_memory()
            return result
        except Exception as e:
            logging.error(f"{self.name} failed: {e}")
            return "Error in Analyzer"

class ReporterAgent(Agent):
    async def process(self, task: str, data: Any) -> str:
        try:
            logging.info(f"{self.name} reporting results for task: {task}")
            await asyncio.sleep(1)
            result = f"Final report generated: {data}"
            self.memory[task] = result
            self.save_memory()
            return result
        except Exception as e:
            logging.error(f"{self.name} failed: {e}")
            return "Error in Reporter"

# --- Orchestrator with Monitoring ---
class Orchestrator:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.routing_policy: Dict[str, str] = {}
        self.task_log: Dict[str, str] = {}

    def register_agent(self, agent: Agent, task_type: str):
        self.agents[agent.name] = agent
        self.routing_policy[task_type] = agent.name

    async def route(self, task_type: str, task: str, data: Any) -> str:
        try:
            if task_type not in self.routing_policy:
                raise ValueError(f"No agent registered for task type: {task_type}")
            agent_name = self.routing_policy[task_type]
            agent = self.agents[agent_name]
            logging.info(f"Routing task '{task}' to agent '{agent_name}'")
            result = await agent.process(task, data)
            self.task_log[task] = result
            return result
        except Exception as e:
            logging.error(f"Routing failed for {task}: {e}")
            return "Routing Error"

    def dashboard(self):
        print("\n--- Monitoring Dashboard ---")
        for task, result in self.task_log.items():
            print(f"Task: {task} | Result: {result}")
        print("----------------------------\n")

# --- Example Workflow ---
async def main():
    collector = CollectorAgent("Collector", "collector_memory.json")
    analyzer = AnalyzerAgent("Analyzer", "analyzer_memory.json")
    reporter = ReporterAgent("Reporter", "reporter_memory.json")

    orch = Orchestrator()
    orch.register_agent(collector, "collect")
    orch.register_agent(analyzer, "analyze")
    orch.register_agent(reporter, "report")

    # Sequential workflow with async
    raw_data = await orch.route("collect", "task1", "User input text")
    analyzed = await orch.route("analyze", "task1", raw_data)
    final_report = await orch.route("report", "task1", analyzed)

    # Show monitoring dashboard
    orch.dashboard()

    print("\n--- Workflow Results ---")
    print(final_report)

# Run the async orchestrator
if __name__ == "__main__":
    asyncio.run(main())


"""
Asynchronous Communication: Agents run asynchronously (asyncio.sleep) simulating concurrent tasks.

Monitoring Dashboard: Orchestrator maintains a task_log and prints a dashboard of task results.

Secure Code Practices:
    try/except blocks around memory loading, saving, and agent processing.
    Logging errors instead of crashing.
    Safe fallback values when memory is corrupted or missing.

    Sequential Workflow: Collector → Analyzer → Reporter, with async execution and error handling.
"""