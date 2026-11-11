"""Memoryless copying-swarm dynamics + oversight-intervention arms. [mean-field, $0]

Models the collusion.wiki mechanism: each tick a cohort of fresh, memoryless agents reads the shared
medium and ADOPTS a convention by conformity-biased copying (prob proportional to prevalence^cs).
Their writes mix into the medium (turnover = cohort/window); old writes age out. A harmful convention
is ENTRENCHED (dominant) when the overseer acts; we ask which lever suppresses the fraction of fresh
writes that are harmful (the live-coordination signal). Deterministic mean-field + finite-cohort
multinomial sampling gives seed-to-seed variance for honest CIs.

Conventions: 0 neutral, 1 HARMFUL, 2 BENIGN (the counter-seed). This is an explicit copying model,
NOT LLM agents (stated honestly); a small real-LLM arm tests whether LLMs copy similarly.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

NEUTRAL, HARM, BENIGN = 0, 1, 2


@dataclass
class Params:
    n_agents: int = 60          # cohort per tick (source influx)
    window: int = 300           # shared-medium size (turnover = n_agents/window)
    copy_strength: float = 1.6  # conformity exponent on prevalence (>1 entrenches the majority)
    innovation: float = 0.03    # fraction of writes that are novel/neutral (noise floor)
    ticks: int = 60
    intervene_at: int = 20
    seed_harm_frac: float = 0.60   # harmful convention is dominant at intervention time
    fitness: tuple = (1.0, 1.0, 1.0)  # benign competes fairly with harmful (no rigged content edge)


def run(p: Params, arm: str = "control", dose: float = 0.0, seed: int = 0) -> np.ndarray:
    """Per-tick harmful ADOPTION = fraction of this tick's fresh writes that are harmful."""
    rng = np.random.default_rng(seed)
    prev = np.array([1 - p.seed_harm_frac, p.seed_harm_frac, 0.0])  # neutral, harm, benign
    replace = p.n_agents / p.window
    fit = np.array(p.fitness)
    out = np.zeros(p.ticks)
    for t in range(p.ticks):
        acting = t >= p.intervene_at
        if arm == "cut_source" and acting:
            out[t] = 0.0                      # no new agents -> no live coordination (infeasible baseline)
            continue
        if arm == "counter_seed" and acting:  # inject committed benign into the medium
            prev = prev.copy(); prev[BENIGN] += dose; prev = prev / prev.sum()
        raw = (prev ** p.copy_strength) * fit
        a = raw / raw.sum()
        a = (1 - p.innovation) * a + p.innovation * np.array([1.0, 0, 0])  # innovation writes neutral
        if arm == "ban_individuals" and acting:  # catch a `dose` fraction of harmful writers (attacks flow)
            a = a.copy(); a[HARM] *= (1 - dose); a = a / a.sum()
        counts = rng.multinomial(p.n_agents, a) / p.n_agents             # finite-cohort sampling
        out[t] = counts[HARM]
        prev = (1 - replace) * prev + replace * counts                   # writes mix into medium
        if arm == "delete_artifacts" and acting:                        # remove a `dose` fraction of harm stock
            prev = prev.copy(); prev[HARM] *= (1 - dose)
        prev = prev / prev.sum()
    return out


def final_adoption(p: Params, arm: str, dose: float, seeds=range(8)) -> tuple[float, float]:
    vals = [float(np.mean(run(p, arm, dose, seed=s)[-10:])) for s in seeds]
    return float(np.mean(vals)), float(np.std(vals))
