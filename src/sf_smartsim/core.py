"""SmartSim core — a role's task-by-task collapse sequence.

Describe a role as tasks, each with `repetition` (how routine it is) and
`judgment` (how much it rests on human judgment), both in [0, 1]. Each task's
moat is `0.7 * judgment + 0.3 * (1 - repetition)`; the Role Viability Index is
the mean moat. The collapse sequence orders tasks from weakest moat to
strongest: the order in which agents are likely to take them over.

    prof = profile_from_tasks("paralegal", load_tasks("paralegal.json"))
    sequence(prof)          # weakest task first
    timeline(load_series("adoption.json"))

`profile(role, seed)` makes up five tasks from seeded random numbers. It
illustrates the scoring for the demo and is not a measurement of any real role.
"""
from __future__ import annotations

import json
import os
import random

from .models import RoleProfile, Task, Timeline

JUDGMENT_WEIGHT = 0.7


def _moat(repetition: float, judgment: float) -> float:
    return round(judgment * JUDGMENT_WEIGHT + (1 - repetition) * (1 - JUDGMENT_WEIGHT), 2)


def _demo():
    p = os.path.join(os.path.dirname(__file__), "..", "..", "demo", "scenario_timeseries.json")
    try:
        return json.load(open(p))["data"]["series"]
    except Exception:
        return [{"tick": t, "collapse_pressure": round(min(1, .05 + t*0.015), 3)} for t in range(60)]


def profile(role: str = "paralegal", seed: int = 7) -> RoleProfile:
    """Five illustrative tasks from seeded random numbers (demo only)."""
    r = random.Random(seed)
    tasks = []
    for i in range(5):
        rep, judg = round(r.random(), 2), round(r.random(), 2)
        tasks.append(Task(f"{role} task {i+1}", rep, judg, _moat(rep, judg)))
    rvi = round(sum(t.moat for t in tasks) / len(tasks), 2)
    return RoleProfile(role, rvi, tasks)


def _unit(value, field, name) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise ValueError(f"task {name!r}: {field} must be a number between 0 and 1")
    return float(value)


def profile_from_tasks(role: str, tasks) -> RoleProfile:
    """Score a real role from [{"name", "repetition", "judgment"}, ...]."""
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("a role needs at least one task")
    out = []
    for i, t in enumerate(tasks):
        if not isinstance(t, dict):
            raise ValueError(f"task {i + 1} must be an object")
        name = str(t.get("name") or t.get("task") or f"task {i + 1}")
        rep = _unit(t.get("repetition"), "repetition", name)
        judg = _unit(t.get("judgment"), "judgment", name)
        out.append(Task(name, rep, judg, _moat(rep, judg)))
    return RoleProfile(role, round(sum(t.moat for t in out) / len(out), 2), out)


def sequence(prof: RoleProfile) -> list[Task]:
    """Tasks from weakest moat to strongest (ties: more repetitive first)."""
    return sorted(prof.tasks, key=lambda t: (t.moat, -t.repetition))


def timeline(series=None) -> Timeline:
    """Collapse pressure over time: your series, or the bundled demo scenario."""
    s = _demo() if series is None else series
    values = []
    for i, x in enumerate(s):
        v = x.get("collapse_pressure") if isinstance(x, dict) else x
        if not isinstance(v, (int, float)) or not 0 <= v <= 1:
            raise ValueError(f"point {i}: collapse_pressure must be between 0 and 1")
        values.append(float(v))
    return Timeline(len(values), values)


def load_tasks(path: str) -> tuple[str, list[dict]]:
    """Read {"role": ..., "tasks": [...]} and return (role, tasks)."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or "tasks" not in data:
        raise ValueError('expected {"role": "...", "tasks": [...]}')
    return str(data.get("role") or os.path.splitext(os.path.basename(path))[0]), data["tasks"]


def load_series(path: str) -> list:
    """Read a list of numbers or of {"tick", "collapse_pressure"} (or the demo's {"data": {"series": [...]}})."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        data = data.get("series") or data.get("data", {}).get("series")
    if not isinstance(data, list):
        raise ValueError("expected a list of points")
    return data
