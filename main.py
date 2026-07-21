"""
Main Application
Voice-to-Terminal Assistant - Local Privacy-Focused CLI Tool
"""

import logging
import sys

from command_executor import CommandExecutor
from config import ALLOWED_COMMANDS, LOG_FILE
from voice_processor import VoiceProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class VoiceTerminalAssistant:
    """Main application class"""

    def __init__(self):
        """Initialize the assistant"""
        self.voice_processor = VoiceProcessor()
        self.command_executor = CommandExecutor()
        self.running = False

    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "=" * 68)
        print("🎙️  VOICE-TO-TERMINAL ASSISTANT".center(68))
        print("=" * 68)
        print("💡 Local • Private • Secure • Portfolio-Ready".center(68))
        print("=" * 68)
        print("\n📋 Available Commands:")
        print("-" * 60)

        for i, (voice_cmd, terminal_cmd) in enumerate(ALLOWED_COMMANDS.items(), 1):
            print(f"  {i:2d}. Say: '{voice_cmd}' → runs: '{terminal_cmd}'")

        print("-" * 60)
        print("\n🎯 Quick Tips:")
        print("  • Speak clearly and naturally")
        print("  • All processing happens locally on your machine")
        print("  • Type 'help' for more options")
        print("  • Type 'quit' to exit")
        print("\n" + "=" * 60 + "\n")

    def display_help(self):
        """Display help information"""
        help_text = """
🆘 HELP MENU
════════════════════════════════════════════════════════════

Commands:
  'voice'      - Activate voice input mode (main feature)
  'type'       - Type a command manually
  'history'    - Show command history
  'clear'      - Clear command history
  'help'       - Show this help menu
  'quit'       - Exit the application

Voice Mode Tips:
  • Speak your command clearly
  • The app will listen for ~10 seconds
  • Press Ctrl+C to cancel listening
  • Commands are processed locally, no external calls

Privacy:
  • All voice processing happens on your machine
  • No data is sent to external servers
  • Commands are only executed locally
  • Check logs in ./logs/voice_terminal.log

════════════════════════════════════════════════════════════
"""
        print(help_text)

    def voice_mode(self):
        """Voice input mode"""
        print("\n🎤 VOICE MODE - Start speaking your command...")
        print("(Press Ctrl+C to cancel)\n")

        try:
            text = self.voice_processor.listen()

            if not text:
                return

            command_intent = self.voice_processor.process_command(text)
            actual_command = self.command_executor.map_command(command_intent)

            if not actual_command:
                print(f"❌ Command not recognized: '{command_intent}'")
                print("💡 Try: 'list', 'current directory', 'date', etc.")
                logger.warning(f"Unrecognized command: {command_intent}")
                return

            print(f"🔧 Will execute: '{actual_command}'")
            confirm = input("Continue? (y/n): ").lower()

            if confirm != "y":
                print("❌ Command cancelled")
                return

            success, output = self.command_executor.execute(actual_command)

            if success:
                if output and output != "Command executed":
                    print(f"\n📤 Output:\n{output}\n")
            else:
                print(f"\n{output}\n")

        except KeyboardInterrupt:
            print("\n\n⏹️  Voice input cancelled")
            logger.info("Voice input cancelled by user")

    def type_mode(self):
        """Manual command typing mode"""
        try:
            command = input("\n📝 Enter command: ").strip()

            if not command:
                return

            print(f"🔧 Will execute: '{command}'")
            confirm = input("Continue? (y/n): ").lower()

            if confirm != "y":
                print("❌ Command cancelled")
                return

            success, output = self.command_executor.execute(command)

            if success:
                if output and output != "Command executed":
                    print(f"\n📤 Output:\n{output}\n")
            else:
                print(f"\n{output}\n")

        except KeyboardInterrupt:
            print("\n\n⏹️  Input cancelled")
            logger.info("Manual input cancelled by user")

    def show_history(self):
        """Display command history"""
        history = self.command_executor.get_history()

        if not history:
            print("\n📭 No command history yet\n")
            return

        print("\n📜 Command History:")
        print("-" * 60)

        for i, cmd in enumerate(history, 1):
            print(f"  {i:2d}. {cmd}")

        print("-" * 60 + "\n")

    def run(self):
        """Main application loop"""
        self.running = True
        self.display_welcome()

        logger.info("Voice Terminal Assistant started")

        while self.running:
            try:
                user_input = input("🎯 Select mode (voice/type/history/help/quit): ").lower().strip()

                if user_input in ["backend", "b"]:
                    # Show backend info and allow switching
                    vp = self.voice_processor
                    available = getattr(vp, "available_backends", [])
                    preferred = getattr(vp, "preferred_backend", None)
                    print(f"\n🔊 Available backends: {', '.join(available) if available else 'none'}")
                    print(f"⭐ Preferred backend: {preferred}\n")
                    if available:
                        choice = input("Set backend (enter name or leave blank to keep): ").strip().lower()
                        if choice:
                            if vp.set_backend(choice):
                                print(f"✅ Backend set to {choice}\n")
                            else:
                                print(f"❌ Backend '{choice}' not available\n")
                    continue

                if user_input in ["voice", "v"]:
                    self.voice_mode()

                elif user_input in ["type", "t"]:
                    self.type_mode()

                elif user_input in ["history", "h"]:
                    self.show_history()

                elif user_input == "clear":
                    self.command_executor.clear_history()
                    print("✅ History cleared\n")

                elif user_input in ["help", "?"]:
                    self.display_help()

                elif user_input in ["quit", "exit", "q"]:
                    self.shutdown()

                else:
                    print("❓ Unknown command. Type 'help' for options.\n")

            except KeyboardInterrupt:
                print("\n\n⏹️  Interrupted by user")
                self.shutdown()

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"❌ Error: {e}\n")

    def shutdown(self):
        """Shutdown the application"""
        print("\n" + "=" * 60)
        print("👋 Thank you for using Voice-to-Terminal Assistant!".center(60))
        print("=" * 60 + "\n")
        logger.info("Voice Terminal Assistant shut down")
        self.running = False
        sys.exit(0)


def main():
    """Entry point"""
    try:
        app = VoiceTerminalAssistant()
        app.run()
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        print(f"\n❌ Critical Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
