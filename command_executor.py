"""
Command Execution Module
Safely executes terminal commands based on voice input
Implements security checks and sandboxing
"""

import logging
import os
import re
import subprocess
from typing import Optional, Tuple

from config import (
    ALLOWED_COMMANDS,
    ENABLE_DESTRUCTIVE_COMMANDS,
    ENABLE_SUDO,
    ERROR_INDICATOR,
    RESTRICTED_COMMANDS,
    SUCCESS_INDICATOR,
)

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Handles command execution with safety checks"""

    def __init__(self):
        """Initialize the command executor"""
        self.command_history = []
        self.max_history = 50

    def map_command(self, voice_input: str) -> Optional[str]:
        """
        Map voice input to actual terminal command

        Args:
            voice_input: Text from voice recognition

        Returns:
            Optional[str]: Mapped command or None if not found
        """
        voice_input = voice_input.lower().strip()

        if voice_input in ALLOWED_COMMANDS:
            return ALLOWED_COMMANDS[voice_input]

        normalized_input = re.sub(r"[^a-z0-9]+", " ", voice_input).strip()
        input_tokens = set(normalized_input.split())

        for key, command in ALLOWED_COMMANDS.items():
            normalized_key = re.sub(r"[^a-z0-9]+", " ", key).strip()
            key_tokens = set(normalized_key.split())

            if normalized_input == normalized_key:
                return command

            if key in voice_input or voice_input in key:
                return command

            if key_tokens & input_tokens:
                return command

            if self._similarity(voice_input, key) > 0.8:
                return command

        return None

    @staticmethod
    def _similarity(s1: str, s2: str) -> float:
        """
        Calculate similarity between two strings (0-1)

        Args:
            s1: First string
            s2: Second string

        Returns:
            float: Similarity score
        """
        longer = s1 if len(s1) > len(s2) else s2
        shorter = s2 if longer == s1 else s1

        if len(longer) == 0:
            return 1.0

        edit_distance = _levenshtein_distance(longer, shorter)
        return (len(longer) - edit_distance) / float(len(longer))

    @staticmethod
    def _resolve_platform_command(command: str, os_name: Optional[str] = None) -> str:
        """Return a platform-appropriate command string for the current shell."""
        if os_name is None:
            os_name = os.name

        if os_name != "nt":
            return command

        windows_mappings = {
            "date": "Get-Date",
            "cal": "Get-Date",
            "pwd": "Get-Location",
            "ls -la": "Get-ChildItem",
            "ls": "Get-ChildItem",
            "uname -a": "whoami",
            "free -h": "Get-Process | Select-Object -First 5",
            "ps aux": "Get-Process",
            "ifconfig": "Get-NetIPConfiguration",
        }

        return windows_mappings.get(command, command)

    def is_safe_command(self, command: str) -> bool:
        """
        Validate command for safety

        Args:
            command: Terminal command to validate

        Returns:
            bool: True if command is safe to execute
        """
        command_lower = command.lower()

        for restricted in RESTRICTED_COMMANDS:
            if restricted.lower() in command_lower:
                logger.warning(f"Restricted command detected: {command}")
                return False

        if "sudo" in command_lower and not ENABLE_SUDO:
            logger.warning("Sudo not enabled")
            return False

        destructive_patterns = [
            r"rm\s+-rf\s+/",
            r"dd\s+if=/dev/zero",
            r":(){:\|:&};:",
        ]

        if not ENABLE_DESTRUCTIVE_COMMANDS:
            for pattern in destructive_patterns:
                if re.search(pattern, command_lower):
                    logger.warning(f"Destructive command detected: {command}")
                    return False

        return True

    def execute(self, command: str) -> Tuple[bool, str]:
        """
        Execute terminal command safely

        Args:
            command: Terminal command to execute

        Returns:
            Tuple[bool, str]: (success, output/error_message)
        """
        try:
            if not self.is_safe_command(command):
                error_msg = "❌ Command rejected for security reasons"
                logger.warning(error_msg)
                return False, error_msg

            self.command_history.append(command)
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)

            command_for_shell = self._resolve_platform_command(command)
            logger.info(f"Executing: {command_for_shell}")

            if os.name == "nt":
                # Use PowerShell on Windows so commands like `date` and `pwd`
                # resolve to PowerShell-native commands instead of hanging.
                result = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-Command", command_for_shell],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            else:
                result = subprocess.run(
                    command_for_shell,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            if result.returncode == 0:
                output = result.stdout.strip() if result.stdout else "Command executed"
                print(f"{SUCCESS_INDICATOR}")
                logger.info(f"Command succeeded: {command}")
                return True, output

            error = result.stderr.strip() if result.stderr else result.stdout
            print(f"{ERROR_INDICATOR}")
            logger.error(f"Command failed: {command}")
            return False, error

        except subprocess.TimeoutExpired:
            error_msg = "❌ Command timed out (30s limit)"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"❌ Execution error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_history(self) -> list:
        """Get command execution history"""
        return self.command_history.copy()

    def clear_history(self):
        """Clear command execution history"""
        self.command_history.clear()
        logger.info("Command history cleared")


def _levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings

    Args:
        s1: First string
        s2: Second string

    Returns:
        int: Edit distance
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
