"""
Jatin K Rai

"""
class Agent:
    def __init__(self, name):
        self.name = name
        self.memory = {}

    def process(self, task):
        # Placeholder logic
        return f"{self.name} processed {task}"
    
#Class

class Orchestrator:
    def __init__(self):
        self.agents = {}
        self.routing_policy = {}

    def register_agent(self, agent, task_type):
        self.agents[agent.name] = agent
        self.routing_policy[task_type] = agent.name

    def route(self, task_type, task):
        agent_name = self.routing_policy.get(task_type)
        agent = self.agents[agent_name]
        result = agent.process(task)
        agent.memory[task_type] = result
        return result

# Usage for sample.
collector = Agent("Collector")
analyzer = Agent("Analyzer")
reporter = Agent("Reporter")

orch = Orchestrator()
orch.register_agent(collector, "collect")
orch.register_agent(analyzer, "analyze")
orch.register_agent(reporter, "report")

print(orch.route("collect", "raw data"))
print(orch.route("analyze", "processed data"))
print(orch.route("report", "final summary"))
