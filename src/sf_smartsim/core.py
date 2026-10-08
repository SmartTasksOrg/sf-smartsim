"""SmartSim core — role/industry collapse timeline."""
import json, os, random
from .models import Task, RoleProfile, Timeline

def _demo():
    p = os.path.join(os.path.dirname(__file__), "..", "..", "demo", "scenario_timeseries.json")
    try:
        return json.load(open(p))["data"]["series"]
    except Exception:
        return [{"tick": t, "collapse_pressure": round(min(1, .05 + t*0.015), 3)} for t in range(60)]

def profile(role: str = "paralegal", seed: int = 7) -> RoleProfile:
    r = random.Random(seed)
    tasks = []
    for i in range(5):
        rep, judg = round(r.random(), 2), round(r.random(), 2)
        moat = round(judg * 0.7 + (1 - rep) * 0.3, 2)
        tasks.append(Task(f"{role} task {i+1}", rep, judg, moat))
    rvi = round(sum(t.moat for t in tasks) / len(tasks), 2)
    return RoleProfile(role, rvi, tasks)

def timeline() -> Timeline:
    s = _demo()
    return Timeline(len(s), [x["collapse_pressure"] for x in s])
