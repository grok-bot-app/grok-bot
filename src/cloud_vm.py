import asyncio
from typing import Dict, Any, Optional

class HumanTakeoverRequired(Exception):
    """Exception raised when an agent requires direct human intervention."""
    pass

class CloudComputer:
    """
    Persistent Cloud VM instance shared across all bots on the account.
    Provides shared browser sessions, filesystem, and terminal.
    """
    def __init__(self, vm_id: str = "vm-cloud-xai-01"):
        self.vm_id = vm_id
        self.filesystem: Dict[str, str] = {}
        self.browser_cookies: Dict[str, str] = {}
        self.active_tab_url: str = "about:blank"
        self._is_human_controlling: bool = False
        self._lock = asyncio.Lock()

    async def navigate_browser(self, url: str) -> str:
        """Simulates opening a page in the shared headless browser."""
        async with self._lock:
            self.active_tab_url = url
            auth_status = "Authenticated" if "session_id" in self.browser_cookies else "Unauthenticated"
            return f"[Browser] Loaded '{url}' (Auth Status: {auth_status})"

    async def execute_terminal(self, command: str) -> str:
        """Executes CLI commands in the cloud environment."""
        async with self._lock:
            # Basic filesystem operations simulation
            if command.startswith("echo "):
                parts = command.split(">")
                if len(parts) == 2:
                    content = parts[0].replace("echo ", "").strip().strip('"')
                    filepath = parts[1].strip()
                    self.filesystem[filepath] = content
                    return f"[Terminal] Written content to {filepath}"
            elif command == "ls":
                return f"[Terminal] Files: {list(self.filesystem.keys())}"
            
            return f"[Terminal] Command output: '{command}' executed successfully."

    async def request_takeover(self, bot_name: str, reason: str) -> None:
        """
        Pauses bot execution and transfers UI control to the user
        for CAPTCHA/2FA or manual authentication.
        """
        self._is_human_controlling = True
        print(f"\n========================================================")
        print(f"🚨 [HUMAN TAKEOVER REQUESTED] Bot: @{bot_name}")
        print(f"   Reason: {reason}")
        print(f"   Status: Waiting for user to complete authorization on screen...")
        
        # Simulate human interaction delay
        await asyncio.sleep(1.5)
        
        # Inject authorization session after human completes login
        self.browser_cookies["session_id"] = "sess_oauth2_verified_token_9981"
        self._is_human_controlling = False
        print(f"✅ [TAKEOVER RESOLVED] Credentials saved to shared VM storage.")
        print(f"========================================================\n")
