from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    name: str
    message: str
    current: int = 0
    total: int = 0
