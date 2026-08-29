import asyncio
from typing import List, Dict, Any, Optional
from cloud_vm import CloudComputer
from skills import Skill

class GrokBot:
    """
    Persistent named agent with isolated role, long-term memory, and contextual awareness.
    """
    def __init__(self, name: str, role: str, description: str, vm: CloudComputer, system: Any):
        self.name = name
        self.role = role
        self.description = description
        self.vm = vm
        self.system = system
        self.memory: List[str] = []
        self.skills: Dict[str, Skill] = {}

    def assign_skill(self, skill: Skill) -> None:
        self.skills[skill.name] = skill

    async def execute_task(self, prompt: str, is_critical: bool = False, params: Dict[str, Any] = None) -> str:
        """Executes a direct human prompt or delegated task."""
        params = params or {}
        print(f"🤖 [Bot @{self.name}] Started processing: '{prompt}'")
        self.memory.append(f"Prompt: {prompt}")

        # Check safety & human approval boundaries
        if is_critical:
            approved = await self.system.request_approval(self.name, prompt)
            if not approved:
                msg = "Task cancelled by human approval policy."
                self.memory.append(msg)
                return msg

        # Check authentication on Cloud VM
        if "session_id" not in self.vm.browser_cookies:
            await self.vm.request_takeover(self.name, "Authentication required for target service")

        # Perform task logic
        res = await self.vm.execute_terminal(f"echo 'Report for {prompt}' > /tmp/report.txt")
        
        output = f"Task completed by @{self.name}. Artifact saved in VM storage."
        self.memory.append(f"Output: {output}")
        return output

    async def mention_bot(self, target_bot: str, task_instructions: str) -> str:
        """Enables direct multi-agent collaboration via @mentions."""
        print(f"💬 [Bot @{self.name}] Mentions @{target_bot}: '{task_instructions}'")
        return await self.system.route_inter_bot_message(
            sender=self.name, recipient=target_bot, message=task_instructions
        )
