"""
Unit Tests for Voice Terminal Assistant
Test command mapping, safety checks, and execution
"""

import importlib
import unittest

from command_executor import CommandExecutor


class TestCommandExecutor(unittest.TestCase):
    """Test command executor functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.executor = CommandExecutor()

    def test_command_mapping(self):
        """Test voice command to terminal mapping"""
        result = self.executor.map_command("list")
        self.assertEqual(result, "ls -la")

        result = self.executor.map_command("current directory")
        self.assertEqual(result, "pwd")

    def test_safety_checks(self):
        """Test command safety validation"""
        self.assertTrue(self.executor.is_safe_command("ls -la"))
        self.assertTrue(self.executor.is_safe_command("pwd"))

        self.assertFalse(self.executor.is_safe_command("rm -rf /"))
        self.assertFalse(self.executor.is_safe_command("dd if=/dev/zero"))

    def test_command_history(self):
        """Test command history tracking"""
        self.executor.command_history.append("ls")
        self.executor.command_history.append("pwd")

        history = self.executor.get_history()
        self.assertEqual(len(history), 2)
        self.assertIn("ls", history)

    def test_fuzzy_matching(self):
        """Test fuzzy command matching"""
        result = self.executor.map_command("list files")
        self.assertIsNotNone(result)

    def test_speech_recognition_import(self):
        """Ensure the speech-recognition stack imports correctly in this environment"""
        speech_module = importlib.import_module("speech_recognition")
        self.assertTrue(hasattr(speech_module, "Recognizer"))

    def test_windows_command_resolution(self):
        """Windows shells should use PowerShell-friendly equivalents for common voice commands"""
        self.assertEqual(self.executor._resolve_platform_command("date", os_name="nt"), "Get-Date")
        self.assertEqual(self.executor._resolve_platform_command("pwd", os_name="nt"), "Get-Location")


class TestCommandSafety(unittest.TestCase):
    """Test command safety features"""

    def setUp(self):
        """Set up test fixtures"""
        self.executor = CommandExecutor()

    def test_no_destructive_commands(self):
        """Verify destructive commands are blocked"""
        dangerous = [
            "rm -rf /",
            "rm -rf /*",
            "dd if=/dev/zero of=/dev/sda",
        ]

        for cmd in dangerous:
            self.assertFalse(
                self.executor.is_safe_command(cmd),
                f"Dangerous command was not blocked: {cmd}",
            )

    def test_allowed_commands_are_safe(self):
        """Verify all configured commands are safe"""
        from config import ALLOWED_COMMANDS

        for command in ALLOWED_COMMANDS.values():
            self.assertTrue(
                self.executor.is_safe_command(command),
                f"Allowed command failed safety check: {command}",
            )


if __name__ == "__main__":
    unittest.main()
