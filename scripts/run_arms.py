"""Control-point feasibility map on the copying swarm (clean stats + the phase results).
Headline: destructive levers' critical dose depends on OBSERVABLE swarm properties
(delete-threshold tracks turnover; ban-threshold tracks conformity); non-destructive flip + source-cut
don't. Committed-minority counter-seed is the known naming-game tip (cited, not claimed novel)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from cutpoint.sim import Params, run

OUT = pathlib.Path("artifacts"); OUT.mkdir(exist_ok=True)
SEEDS = range(40)


def finals(p, arm, dose):
    return np.array([np.mean(run(p, arm, dose, seed=s)[-10:]) for s in SEEDS])


def summ(p, arm, dose):
    v = finals(p, arm, dose)
    return v.mean(), np.mean(v > 0.5), (np.percentile(v, 2.5), np.percentile(v, 97.5))


def critical_dose(p, arm, doses=np.round(np.arange(0, 0.96, 0.05), 2)):
    for d in doses:
        if finals(p, arm, d).mean() < 0.1:
            return float(d)
    return None


print("=== clean stats (n_agents=200, 40 seeds), report mean / frac-fixated / 95% CI ===")
p = Params(n_agents=200)
for arm, dose in [("control", 0), ("cut_source", 0), ("delete_artifacts", 0.5),
                  ("ban_individuals", 0.5), ("counter_seed", 0.1)]:
    m, f, ci = summ(p, arm, dose)
    print(f"  {arm:16} dose={dose:<4} mean={m:.3f} frac_fixated={f:.2f} CI=[{ci[0]:.3f},{ci[1]:.3f}]")

print("\n=== PHASE 1: delete critical dose TRACKS TURNOVER (n/window) - emergent race ===")
for window in [500, 1000, 2000]:
    pp = Params(n_agents=200, window=window)
    turnover = 200 / window
    cd = critical_dose(pp, "delete_artifacts")
    print(f"  turnover={turnover:.2f} (window={window}) -> critical delete dose = {cd}")

print("\n=== PHASE 2: ban critical dose TRACKS CONFORMITY (copy_strength) ===")
for cs in [1.0, 1.6, 2.0, 2.5, 3.0]:
    pp = Params(n_agents=200, copy_strength=cs)
    cb = critical_dose(pp, "ban_individuals")
    cdl = critical_dose(pp, "delete_artifacts")
    print(f"  copy_strength={cs} -> critical ban dose = {cb} | critical delete dose = {cdl}")

print("\n=== PHASE 3: counter-seed tipping point (naming-game committed minority - CITE, not novel) ===")
for cs in [1.0, 1.6, 2.5]:
    pp = Params(n_agents=200, copy_strength=cs)
    cc = critical_dose(pp, "counter_seed")
    print(f"  copy_strength={cs} -> critical counter-seed committed fraction = {cc}")

# ---- the operator feasibility map figure ----
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    css = [1.0, 1.6, 2.0, 2.5, 3.0]
    del_c = [critical_dose(Params(n_agents=200, copy_strength=c), "delete_artifacts") for c in css]
    ban_c = [critical_dose(Params(n_agents=200, copy_strength=c), "ban_individuals") for c in css]
    seed_c = [critical_dose(Params(n_agents=200, copy_strength=c), "counter_seed") for c in css]
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for ys, lab, mk in [(del_c, "delete-artifacts (destructive)", "o"),
                        (ban_c, "ban-individuals (destructive)", "s"),
                        (seed_c, "counter-seed (non-destructive)", "^")]:
        ys = [y if y is not None else 1.05 for y in ys]
        ax.plot(css, ys, marker=mk, label=lab)
    ax.axhline(1.0, ls="--", color="grey", lw=1); ax.text(1.0, 1.01, "infeasible (dose>1)", color="grey")
    ax.set_xlabel("conformity (copy_strength) - an observable swarm property")
    ax.set_ylabel("minimum dose for the lever to work")
    ax.set_title("Control-point feasibility map: which lever is cheap enough, by swarm conformity")
    ax.legend(); fig.tight_layout(); fig.savefig(OUT / "cutpoint_feasibility.png", dpi=130)
    print("\nsaved artifacts/cutpoint_feasibility.png")
except Exception as e:
    print("figure error:", e)
