"""Minimal compatibility shim for the audioop module on Windows.

Python builds on Windows may omit the standard-library audioop module.
SpeechRecognition imports it for audio processing even when the app only needs
basic microphone setup. This shim provides the small subset needed for import
and lightweight runtime behavior.
"""

from __future__ import annotations

import struct
from typing import Any


class error(Exception):
    """Raised for unsupported audio operations."""


def avg(frame: bytes, width: int) -> int:
    if not frame:
        return 0
    if width == 1:
        return int(sum(frame) / len(frame))
    if width == 2:
        values = struct.unpack(f"{len(frame)//2}h", frame)
        return int(sum(values) / len(values))
    raise error("unsupported width")


def max(frame: bytes, width: int) -> int:
    if not frame:
        return 0
    if width == 1:
        return max(frame)
    if width == 2:
        values = struct.unpack(f"{len(frame)//2}h", frame)
        return max(values)
    raise error("unsupported width")


def rms(frame: bytes, width: int) -> int:
    if not frame:
        return 0
    if width == 1:
        values = [b for b in frame]
    elif width == 2:
        values = list(struct.unpack(f"{len(frame)//2}h", frame))
    else:
        raise error("unsupported width")
    return int((sum(v * v for v in values) / len(values)) ** 0.5)


def tomono(frame: bytes, width: int, lfactor: float, rfactor: float) -> bytes:
    return frame


def lin2lin(frame: bytes, from_width: int, to_width: int) -> bytes:
    return frame


def ulaw2lin(frame: bytes, width: int) -> bytes:
    return frame


def mul(frame: bytes, width: int, factor: float) -> bytes:
    return frame


def findfit(frame: bytes, width: int, *args: Any, **kwargs: Any) -> int:
    return 0


def findmax(frame: bytes, width: int, *args: Any, **kwargs: Any) -> int:
    return 0


def findfactor(frame: bytes, width: int, *args: Any, **kwargs: Any) -> int:
    return 0
