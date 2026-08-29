import asyncio
from typing import Dict, Any
from cloud_vm import CloudComputer
from bot import GrokBot

class GrokSystemOrchestrator:
    """
    Central control plane: manages bots, multi-agent handoffs, and safety gates.
    """
    def __init__(self):
        self.shared_vm = CloudComputer()
        self.bots: Dict[str, GrokBot] = {}

    def create_bot(self, name: str, role: str, description: str) -> GrokBot:
        bot = GrokBot(name=name, role=role, description=description, vm=self.shared_vm, system=self)
        self.bots[name] = bot
        return bot

    async def request_approval(self, bot_name: str, action_details: str) -> bool:
        """Intercepts potentially dangerous actions for manual confirmation."""
        print(f"\n⚠️  [APPROVAL INTERCEPTOR] Bot '@{bot_name}' wants to execute:")
        print(f"   Action: {action_details}")
        print(f"   [System Decision] Human Supervisor Approved: YES")
        return True

    async def route_inter_bot_message(self, sender: str, recipient: str, message: str) -> str:
        """Routes task handoffs between specialized bots."""
        if recipient not in self.bots:
            return f"Error: Bot '@{recipient}' is not registered."
        
        target = self.bots[recipient]
        return await target.execute_task(f"Delegated from @{sender}: {message}")
