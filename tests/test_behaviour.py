"""Behaviour of core.profile and core.timeline. profile() uses seeded random task values, so it is
an illustration of the scoring, not a measurement of a real role."""
import os
import types

from sf_smartsim import core


def test_profile_is_deterministic_for_a_seed():
    assert core.profile("paralegal", seed=7) == core.profile("paralegal", seed=7)
    assert core.profile("paralegal", seed=7) != core.profile("paralegal", seed=8)


def test_each_task_moat_follows_the_formula():
    p = core.profile("analyst", seed=3)
    assert len(p.tasks) == 5 and p.role == "analyst"
    for t in p.tasks:
        assert t.moat == round(t.judgment * 0.7 + (1 - t.repetition) * 0.3, 2)
        assert 0 <= t.moat <= 1
    assert p.role_viability_index == round(sum(t.moat for t in p.tasks) / 5, 2)


def test_task_names_carry_the_role():
    assert [t.name for t in core.profile("nurse").tasks] == [f"nurse task {i}" for i in range(1, 6)]


def test_timeline_reads_the_bundled_scenario():
    tl = core.timeline()
    assert tl.ticks == len(tl.collapse_pressure) == 60
    assert tl.collapse_pressure[0] == 0.05


def test_without_the_scenario_file_a_built_in_ramp_is_used(monkeypatch):
    fake_path = types.SimpleNamespace(join=lambda *a: "/nonexistent/scenario_timeseries.json", dirname=os.path.dirname)
    monkeypatch.setattr(core, "os", types.SimpleNamespace(path=fake_path))
    tl = core.timeline()
    assert tl.ticks == 60
    assert tl.collapse_pressure[:3] == [0.05, 0.065, 0.08]
    assert max(tl.collapse_pressure) <= 1
