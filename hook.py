from typing import Dict, Any
from datetime import datetime


class LifecycleHooks:
    def __init__(self, context):
        self.context = context
    
    async def on_agent_start(self, agent_name: str, user_input: str):
        print(f"🔹 [{datetime.now().isoformat()}] Agent {agent_name} started processing: {user_input[:50]}...")
        self.context.add_progress_log("agent_start", f"{agent_name} started")
    
    async def on_tool_start(self, tool_name: str, parameters: Dict[str, Any]):
        print(f"🛠️  [{datetime.now().isoformat()}] Tool {tool_name} executing with params: {parameters}")
        self.context.add_progress_log("tool_execution", f"{tool_name} started")
    
    async def on_tool_end(self, tool_name: str, result: Any):
        print(f"✅ [{datetime.now().isoformat()}] Tool {tool_name} completed")
        self.context.add_progress_log("tool_execution", f"{tool_name} completed")
    
    async def on_handoff(self, from_agent: str, to_agent: str, reason: str):
        print(f"🔄 [{datetime.now().isoformat()}] Handoff from {from_agent} to {to_agent}: {reason}")
        self.context.add_handoff_log(f"From {from_agent} to {to_agent}: {reason}")
    
    async def on_error(self, component: str, error: Exception):
        print(f"❌ [{datetime.now().isoformat()}] Error in {component}: {str(error)}")
        self.context.add_progress_log("error", f"{component}: {str(error)}")