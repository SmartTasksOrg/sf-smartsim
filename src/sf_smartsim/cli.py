"""SmartSim CLI.

    sf-smartsim --demo
    sf-smartsim ROLE.json [--series SERIES.json] [--json]

ROLE.json: {"role": "paralegal", "tasks": [{"name": "doc review",
"repetition": 0.9, "judgment": 0.2}, ...]}.
"""
import argparse
import json
import os
import sys
from dataclasses import asdict

from . import core
from ._version import __version__

BANNER = f"\n🦔 SmartSim {__version__}  ·  IAIso §8 · Foresight"
FOOTER = "\nBacked by IAIso §8 · Foresight · part of the Smart* family · https://smarttasks.cloud\n"


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def _spark(values):
    step = max(1, len(values) // 32)
    return "".join("▁▂▃▅▆▇█"[min(6, int(v * 7))] for v in values[::step])


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartSim {__version__}"); return 0
    if not argv or "--demo" in argv:
        print(BANNER); print(core_demo()); print(FOOTER); return 0

    ap = argparse.ArgumentParser(prog="sf-smartsim")
    ap.add_argument("role", help="JSON file describing the role's tasks")
    ap.add_argument("--series", default=None, help="JSON file of collapse pressure over time")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    role, tasks = core.load_tasks(a.role)
    prof = core.profile_from_tasks(role, tasks)
    seq = core.sequence(prof)
    tl = core.timeline(core.load_series(a.series)) if a.series else None
    if a.json:
        print(json.dumps({"profile": asdict(prof), "sequence": [t.name for t in seq],
                          "timeline": asdict(tl) if tl else None}, indent=2, ensure_ascii=False))
        return 0
    print(f"role: {prof.role}   Role Viability Index: {prof.role_viability_index}")
    print("collapse sequence (weakest moat first):")
    for i, t in enumerate(seq, 1):
        print(f"  {i}. {t.name:<24} moat {t.moat}")
    if tl:
        print(f"collapse pressure over {tl.ticks} points: {_spark(tl.collapse_pressure)}")
    return 0


def core_demo() -> str:
    return _DEMO()


def _DEMO():
    prof = core.profile("paralegal")
    tl = core.timeline()
    spark = _spark(tl.collapse_pressure)
    out = [f"role: {prof.role} (illustrative tasks)   Role Viability Index: {prof.role_viability_index}"]
    for tk in prof.tasks:
        out.append(f"  task {tk.name:<16} moat {tk.moat}")
    out.append(f"collapse pressure over {tl.ticks} ticks: {spark}")
    return "\n".join(out)

if __name__ == "__main__":
    sys.exit(main())
