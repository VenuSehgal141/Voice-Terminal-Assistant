"""
Voice Processing Module
Handles speech recognition locally using PocketSphinx/Google Speech Recognition
No external voice data is sent anywhere
"""

import logging
import os

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - environment-dependent
    sr = None
    pocketsphinx = None
else:
    try:
        import pocketsphinx
    except Exception:
        pocketsphinx = None

from config import (
    RECOGNITION_LANGUAGE,
    AUDIO_TIMEOUT,
    RECOGNITION_TIMEOUT,
    LISTEN_INDICATOR,
    PROCESSING_INDICATOR,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sr is None:
    UnknownValueError = RuntimeError
    RequestError = RuntimeError
else:
    UnknownValueError = sr.UnknownValueError
    RequestError = sr.RequestError


class VoiceProcessor:
    """Handles all voice input and recognition"""

    def __init__(self):
        """Initialize the voice processor"""
        if sr is None:
            self.recognizer = None
            self.microphone = None
            logger.warning("speech_recognition is not installed; voice input is disabled")
            return

        # Recognizer
        self.recognizer = sr.Recognizer()

        # Try to create a Microphone; if it fails, degrade gracefully
        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            logger.warning(f"Microphone unavailable: {e}")
            self.microphone = None

        # Adjust recognizer settings for better accuracy (when microphone exists)
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True

        # dotenv support for persisting preferred backend
        try:
            from dotenv import load_dotenv, set_key, find_dotenv  # type: ignore
        except Exception:  # pragma: no cover - optional dependency
            load_dotenv = None
            set_key = None
            find_dotenv = None

        # Detect available backends and choose default
        self.available_backends = self._detect_backends()
        self.preferred_backend = os.environ.get("VOICE_BACKEND")
        if not self.preferred_backend:
            # prefer sphinx if available, otherwise google
            self.preferred_backend = "sphinx" if "sphinx" in self.available_backends else "google"
        logger.info(f"Available speech backends: {self.available_backends}; preferred: {self.preferred_backend}")

    def listen(self) -> str:
        """
        Listen to microphone input and convert to text

        Returns:
            str: Recognized text from speech
        """
        if self.recognizer is None or self.microphone is None:
            print("❌ Voice input is unavailable because the speech recognition package is not installed.")
            return ""

        try:
            print(f"\n{LISTEN_INDICATOR}")

            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.listen(
                    source,
                    timeout=AUDIO_TIMEOUT,
                    phrase_time_limit=AUDIO_TIMEOUT,
                )

            print(f"{PROCESSING_INDICATOR}")

            text = self._recognize_speech(audio_data)

            if text:
                print(f"📝 Heard: '{text}'")
                logger.info(f"Voice input recognized: {text}")
                return text

            logger.warning("No speech recognized")
            print("❌ No speech recognized. Try again.")
            return ""

        except UnknownValueError:
            logger.warning("Speech could not be understood")
            print("❌ Could not understand speech. Please speak clearly.")
            return ""

        except RequestError as e:
            logger.error(f"Error with speech recognition: {e}")
            print(f"❌ Recognition error: {e}")
            return ""

        except Exception as e:
            logger.error(f"Unexpected error during voice processing: {e}")
            print(f"❌ Error: {e}")
            return ""

    def _recognize_speech(self, audio_data) -> str:
        """
        Try to recognize speech using available methods

        Args:
            audio_data: Audio data from microphone

        Returns:
            str: Recognized text
        """
        try:
            # Try the preferred backend first
            backends = [self.preferred_backend] + [b for b in self.available_backends if b != self.preferred_backend]

            for backend in backends:
                if backend == "sphinx":
                    # pocketsphinx offline recognition
                    try:
                        text = self.recognizer.recognize_sphinx(audio_data)
                        logger.info("Using PocketSphinx for recognition")
                        return text.lower()
                    except Exception:
                        logger.debug("PocketSphinx failed or unavailable; trying next backend")

                elif backend == "google":
                    try:
                        text = self.recognizer.recognize_google(audio_data, language=RECOGNITION_LANGUAGE)
                        logger.info("Using Google Speech Recognition")
                        return text.lower()
                    except Exception:
                        logger.debug("Google recognition failed; trying next backend")

            return ""

        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return ""

    def _detect_backends(self) -> list:
        """Detect available speech backends on this system."""
        backends = []
        # PocketSphinx (offline) if module available and recognizer supports it
        try:
            if pocketsphinx is not None and hasattr(self.recognizer, "recognize_sphinx"):
                backends.append("sphinx")
        except Exception:
            pass

        # Google (online) always available if recognizer supports it
        try:
            if hasattr(self.recognizer, "recognize_google"):
                backends.append("google")
        except Exception:
            pass

        return backends

    def set_backend(self, backend: str) -> bool:
        """Set the preferred backend if available.

        Returns True if set, False if invalid.
        """
        if backend not in self.available_backends:
            logger.warning(f"Requested backend not available: {backend}")
            return False

        self.preferred_backend = backend
        logger.info(f"Preferred backend set to: {backend}")

        # Persist to .env if possible (best-effort)
        try:
            env_path = None
            if set_key and find_dotenv:
                env_path = find_dotenv() or ".env"
                set_key(env_path, "VOICE_BACKEND", backend)
            else:
                # Fallback: simple .env updater
                env_path = os.path.join(os.getcwd(), ".env")
                lines = []
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                key_found = False
                for i, line in enumerate(lines):
                    if line.strip().startswith("VOICE_BACKEND="):
                        lines[i] = f"VOICE_BACKEND={backend}\n"
                        key_found = True
                        break

                if not key_found:
                    lines.append(f"VOICE_BACKEND={backend}\n")

                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

        except Exception:
            logger.debug("Could not persist VOICE_BACKEND to .env (ignored)")

        # Update runtime environment
        os.environ["VOICE_BACKEND"] = backend

        return True
        return True

    def process_command(self, text: str) -> str:
        """
        Process recognized text and extract command intent

        Args:
            text: Recognized text

        Returns:
            str: Extracted command
        """
        text = text.lower().strip()

        fillers = ["please", "can you", "could you", "would you", "can i", "execute"]
        for filler in fillers:
            text = text.replace(filler, "").strip()

        return text
