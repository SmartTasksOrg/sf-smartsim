"""UML data objects for SmartSim — the diagram in the README is these classes."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Task:
    name: str
    repetition: float
    judgment: float
    moat: float

@dataclass
class RoleProfile:
    role: str
    role_viability_index: float
    tasks: list[Task]

@dataclass
class Timeline:
    ticks: int
    collapse_pressure: list[float]
