import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable
from cloud_vm import CloudComputer

@dataclass
class SkillStep:
    action_type: str  # "browser", "terminal", "file"
    command: str
    expected_output: str

@dataclass
class Skill:
    """Reusable workflow definition executable by any authorized bot."""
    name: str
    description: str
    steps: List[SkillStep]
    requires_approval: bool = False

    async def execute(self, vm: CloudComputer, parameters: Dict[str, Any]) -> str:
        """Executes all recorded skill steps inside the Cloud Computer."""
        results = []
        for idx, step in enumerate(self.steps, start=1):
            formatted_cmd = step.command.format(**parameters)
            if step.action_type == "browser":
                res = await vm.navigate_browser(formatted_cmd)
            elif step.action_type == "terminal":
                res = await vm.execute_terminal(formatted_cmd)
            else:
                res = f"[Skill Step {idx}] Performed action: {formatted_cmd}"
            results.append(res)
            await asyncio.sleep(0.2)
        return f"Skill '{self.name}' completed successfully. Details: {results}"


class SkillRecorder:
    """Teaches skills by recording user demonstration on the Cloud Computer."""
    @staticmethod
    async def teach_task_by_demo(skill_name: str, raw_actions: List[Dict[str, str]]) -> Skill:
        print(f"[SkillRecorder] Learning routine '{skill_name}' from demonstration...")
        steps = []
        for act in raw_actions:
            steps.append(SkillStep(
                action_type=act["type"],
                command=act["cmd"],
                expected_output="OK"
            ))
            await asyncio.sleep(0.1)
        
        print(f"[SkillRecorder] Skill '{skill_name}' compiled with {len(steps)} steps.")
        return Skill(name=skill_name, description=f"Auto-generated skill: {skill_name}", steps=steps)
