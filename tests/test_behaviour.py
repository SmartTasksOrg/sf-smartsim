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


import json

import pytest

ROLE = {"role": "paralegal", "tasks": [
    {"name": "doc review", "repetition": 0.9, "judgment": 0.2},
    {"name": "client counsel", "repetition": 0.2, "judgment": 0.9},
    {"name": "filing", "repetition": 1.0, "judgment": 0.0}]}


def test_a_real_role_is_scored_from_its_tasks():
    prof = core.profile_from_tasks(ROLE["role"], ROLE["tasks"])
    moats = {t.name: t.moat for t in prof.tasks}
    assert moats == {"doc review": 0.17, "client counsel": 0.87, "filing": 0.0}
    assert prof.role_viability_index == 0.35


def test_the_collapse_sequence_starts_with_the_weakest_task():
    prof = core.profile_from_tasks("p", ROLE["tasks"])
    assert [t.name for t in core.sequence(prof)] == ["filing", "doc review", "client counsel"]


@pytest.mark.parametrize("tasks", [[], [{"name": "x", "repetition": 2, "judgment": 0}],
                                   [{"name": "x", "repetition": 0.5}], ["not a task"]])
def test_tasks_are_validated(tasks):
    with pytest.raises(ValueError):
        core.profile_from_tasks("r", tasks)


def test_your_own_series_is_used_and_validated():
    assert core.timeline([0.1, 0.2, 0.4]).collapse_pressure == [0.1, 0.2, 0.4]
    assert core.timeline([{"tick": 0, "collapse_pressure": 0.3}]).ticks == 1
    with pytest.raises(ValueError):
        core.timeline([1.5])


def test_cli_reads_a_role_file(tmp_path, capsys):
    from sf_smartsim import cli
    f, series = tmp_path / "paralegal.json", tmp_path / "s.json"
    f.write_text(json.dumps(ROLE))
    series.write_text(json.dumps([0.1, 0.5, 0.9]))
    assert cli.main([str(f), "--series", str(series), "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["sequence"][0] == "filing" and out["timeline"]["ticks"] == 3
