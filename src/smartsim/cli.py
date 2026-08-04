"""SmartSim CLI — run `smartsim --demo`."""
import os, sys, json
from . import core
from ._version import __version__


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartSim {__version__}"); return 0
    demo = "--demo" in argv or not argv
    print(f"\n🦔 SmartSim {__version__}  ·  IAIso §8 · Foresight")
    result = core_demo()
    print(result)
    print(f"\nBacked by IAIso §8 · Foresight · part of the Smart* family · https://smarttasks.cloud\n")
    return 0


def core_demo() -> str:
    return _DEMO()


def _DEMO():
    prof = core.profile("paralegal")
    tl = core.timeline()
    spark = "".join("▁▂▃▅▆▇█"[min(6, int(v*7))] for v in tl.collapse_pressure[::max(1,len(tl.collapse_pressure)//32)])
    out = [f"role: {prof.role}   Role Viability Index: {prof.role_viability_index}"]
    for tk in prof.tasks:
        out.append(f"  task {tk.name:<16} moat {tk.moat}")
    out.append(f"collapse pressure over {tl.ticks} ticks: {spark}")
    return "\n".join(out)

if __name__ == "__main__":
    sys.exit(main())
