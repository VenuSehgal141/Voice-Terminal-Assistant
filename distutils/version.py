"""Compatibility implementation of distutils.version.LooseVersion."""

from __future__ import annotations

from packaging.version import InvalidVersion, Version


class LooseVersion:
    """Lightweight version object that supports comparison."""

    def __init__(self, vstring: str = "0") -> None:
        self.vstring = str(vstring)
        try:
            self._version = Version(self.vstring)
        except InvalidVersion:
            self._version = Version("0")

    def __str__(self) -> str:
        return self.vstring

    def __repr__(self) -> str:
        return f"LooseVersion('{self.vstring}')"

    def __lt__(self, other: object) -> bool:
        return self._version < Version(str(other))

    def __le__(self, other: object) -> bool:
        return self._version <= Version(str(other))

    def __eq__(self, other: object) -> bool:
        return self._version == Version(str(other))

    def __ne__(self, other: object) -> bool:
        return self._version != Version(str(other))

    def __gt__(self, other: object) -> bool:
        return self._version > Version(str(other))

    def __ge__(self, other: object) -> bool:
        return self._version >= Version(str(other))
