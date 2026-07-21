"""
Configuration for Voice-to-Terminal Assistant
All settings in one place for easy customization
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Audio settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 1024
AUDIO_TIMEOUT = 10  # seconds to listen for command

# Speech recognition settings
RECOGNITION_LANGUAGE = "en-US"
RECOGNITION_TIMEOUT = 10

# Command settings
ALLOWED_COMMANDS = {
    "list": "ls -la",
    "show files": "ls -la",
    "print working directory": "pwd",
    "current directory": "pwd",
    "make directory": "mkdir",
    "remove file": "rm",
    "copy": "cp",
    "move": "mv",
    "find": "find",
    "grep": "grep",
    "disk usage": "du -sh",
    "system info": "uname -a",
    "memory": "free -h",
    "processes": "ps aux",
    "network": "ifconfig",
    "date": "date",
    "calendar": "cal",
    "weather": "curl wttr.in",
}

# Safety settings
RESTRICTED_COMMANDS = [
    "rm -rf /",
    "dd if=/dev/zero",
    "fork bomb",
    ":(){:|:&};:",
    "sudo rm",
]

ENABLE_SUDO = False
ENABLE_DESTRUCTIVE_COMMANDS = False

# Logging
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "voice_terminal.log"

# Voice settings
LISTEN_INDICATOR = "🎤 Listening..."
PROCESSING_INDICATOR = "⚙️  Processing..."
SUCCESS_INDICATOR = "✅ Command executed"
ERROR_INDICATOR = "❌ Error"
