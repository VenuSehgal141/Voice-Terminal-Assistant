"""Minimal compatibility shim for the aifc module on Windows.

Some Python environments, especially Windows builds, do not ship the
standard-library aifc module. SpeechRecognition imports it at module import
time even though microphone capture does not need it. This shim provides a
lightweight fallback so the application can still initialize.
"""

from __future__ import annotations

import wave
from typing import Any


class Error(Exception):
    """Raised for AIFF/AIFC-related issues."""


class _AifcProxy:
    """Simple wrapper over a wave file object."""

    def __init__(self, file: Any, mode: str = "rb") -> None:
        self._wave = wave.open(file, mode)

    def readframes(self, nframes: int) -> bytes:
        return self._wave.readframes(nframes)

    def getnframes(self) -> int:
        return self._wave.getnframes()

    def getframerate(self) -> int:
        return self._wave.getframerate()

    def getnchannels(self) -> int:
        return self._wave.getnchannels()

    def getsampwidth(self) -> int:
        return self._wave.getsampwidth()

    def close(self) -> None:
        self._wave.close()


def open(file: Any, mode: str = "rb") -> _AifcProxy:
    return _AifcProxy(file, mode)
