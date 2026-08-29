import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Deque
from skills import Skill
from cloud_vm import CloudComputer

@dataclass
class ExecutionRecord:
    timestamp: str
    status: str
    log: str

class Routine:
    """
    Scheduled or event-triggered automation job.
    Maintains a rolling audit log capped at the last 20 execution records.
    """
    def __init__(self, name: str, bot_name: str, skill: Skill, schedule_cron: str):
        self.name = name
        self.bot_name = bot_name
        self.skill = skill
        self.schedule_cron = schedule_cron
        self.is_active: bool = True
        # Strict cap of last 20 execution history records
        self.history: Deque[ExecutionRecord] = deque(maxlen=20)

    def log_run(self, status: str, result_log: str) -> None:
        record = ExecutionRecord(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status=status,
            log=result_log
        )
        self.history.append(record)

class RoutineScheduler:
    """Background engine handling routines execution without interrupting active UI."""
    def __init__(self, vm: CloudComputer):
        self.vm = vm
        self.routines: Dict[str, Routine] = {}

    def register_routine(self, routine: Routine) -> None:
        self.routines[routine.name] = routine

    async def run_routine_now(self, routine_name: str, params: dict) -> None:
        routine = self.routines.get(routine_name)
        if not routine or not routine.is_active:
            return

        print(f"[RoutineScheduler] Triggering background routine '{routine.name}' for @{routine.bot_name}...")
        try:
            output = await routine.skill.execute(self.vm, params)
            routine.log_run("SUCCESS", output)
            print(f"🟢 [Routine Success] '{routine.name}' recorded in history. (Total logs: {len(routine.history)})")
        except Exception as err:
            routine.log_run("FAILED", str(err))
            print(f"🔴 [Routine Failed] '{routine.name}': {err}")
