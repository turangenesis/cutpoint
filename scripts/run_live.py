"""Full live-swarm oversight run: control / delete / monitor / monitor-vs-evasive, seeds + CIs.
Saves artifacts/live_results.json + figure. Needs OPENROUTER_API_KEY."""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from cutpoint.swarm_live import run, chat, AGENT_PROMPT, AGENT_PROMPT_EVASIVE, MONITOR_PROMPT, GOAL

OUT = pathlib.Path("artifacts"); OUT.mkdir(exist_ok=True)
AG = "qwen/qwen-2.5-7b-instruct"; MON = "mistralai/mistral-small-24b-instruct-2501"
SEEDS = range(6); N, T = 5, 8


def agent_normal(ctx, s):
    try: return chat(AG, AGENT_PROMPT.format(goal=GOAL, board=ctx)).strip().splitlines()[0]
    except Exception: return "entry: (err)"
def agent_evasive(ctx, s):
    try: return chat(AG, AGENT_PROMPT_EVASIVE.format(goal=GOAL, board=ctx)).strip().splitlines()[0]
    except Exception: return "entry: (err)"
def monitor(entry):
    try: return chat(MON, MONITOR_PROMPT.format(entry=entry), temperature=0.0, max_tokens=4)
    except Exception: return "ALLOW"


CONDS = [("control", agent_normal, "control"), ("delete", agent_normal, "delete"),
         ("monitor", agent_normal, "monitor"), ("monitor_vs_evasive", agent_evasive, "monitor")]
results = {}
for name, ag, arm in CONDS:
    curves = [run(ag, monitor, arm=arm, n_agents=N, ticks=T, seed=s) for s in SEEDS]
    arr = np.array(curves)
    finals = arr[:, -3:].mean(axis=1)                     # mean convergence over last 3 ticks, per seed
    mean, lo, hi = finals.mean(), np.percentile(finals, 2.5), np.percentile(finals, 97.5)
    results[name] = dict(mean=float(mean), lo=float(lo), hi=float(hi),
                         curve=arr.mean(0).round(3).tolist(), finals=finals.round(3).tolist())
    print(f"{name:20} final coordination = {mean:.2f}  CI[{lo:.2f},{hi:.2f}]  curve={results[name]['curve']}", flush=True)
(OUT / "live_results.json").write_text(json.dumps(results, indent=2))

# ---- figure ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
for name in results:
    ax1.plot(range(1, T + 1), results[name]["curve"], marker="o", label=name)
ax1.axvline(1.5, ls=":", color="grey"); ax1.set_xlabel("round"); ax1.set_ylabel("coordination (shared-codeword convergence)")
ax1.set_title("Live LLM swarm: coordination under each oversight lever"); ax1.legend(fontsize=8); ax1.set_ylim(-0.03, 1.05)
names = list(results); vals = [results[n]["mean"] for n in names]
err = [[results[n]["mean"] - results[n]["lo"] for n in names], [results[n]["hi"] - results[n]["mean"] for n in names]]
ax2.bar(names, vals, yerr=err, capsize=5, color=["grey", "tab:red", "tab:green", "tab:orange"])
ax2.set_ylabel("final coordination (95% CI)"); ax2.set_title("Delete fails (re-derivation); medium-monitor holds")
ax2.tick_params(axis="x", rotation=20); ax2.set_ylim(0, 1.05)
fig.tight_layout(); fig.savefig(OUT / "live_oversight.png", dpi=130)
print("saved artifacts/live_oversight.png + live_results.json", flush=True)
