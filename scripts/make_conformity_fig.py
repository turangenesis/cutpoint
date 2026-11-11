"""Conformity figure from the measured values (30 trials/f, log prompt, bootstrap CIs)."""
import pathlib, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = pathlib.Path("artifacts"); OUT.mkdir(exist_ok=True)

fs = np.array([0.0, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 1.0])
curves = {  # P(X | f) measured
    "Qwen-2.5-7B":        [0.00, 0.00, 0.23, 0.30, 0.67, 0.80, 0.97, 1.00],
    "Mistral-Small-24B":  [0.00, 0.21, 0.31, 0.48, 0.67, 0.38, 0.68, 1.00],
    "Llama-3.1-8B":       [0.00, 0.28, 0.60, 0.47, 0.38, 0.54, 0.80, 1.00],
}
cs = {"Qwen-2.5-7B": (2.01, 1.64, 2.67), "Mistral-Small-24B": (0.57, 0.28, 0.94),
      "Llama-3.1-8B": (0.47, 0.18, 0.78)}
colors = {"Qwen-2.5-7B": "tab:red", "Mistral-Small-24B": "tab:blue", "Llama-3.1-8B": "tab:green"}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
ax1.plot([0, 1], [0, 1], ls="--", color="grey", lw=1, label="cs = 1 (proportional)")
for m, ys in curves.items():
    ax1.plot(fs, ys, marker="o", color=colors[m], label=m)
ax1.set_xlabel("prevalence f of a convention in the peer context")
ax1.set_ylabel("P(the LLM adopts it)")
ax1.set_title("Convention adoption vs prevalence (n=30/point)"); ax1.legend(fontsize=8)

names = list(cs); vals = [cs[n][0] for n in names]
lo = [cs[n][0] - cs[n][1] for n in names]; hi = [cs[n][2] - cs[n][0] for n in names]
ax2.bar(names, vals, yerr=[lo, hi], capsize=6, color=[colors[n] for n in names])
ax2.axhline(1.0, ls="--", color="black", lw=1); ax2.text(2.1, 1.03, "cs = 1 (no conformity)", fontsize=8)
ax2.set_ylabel("conformity exponent cs  (95% CI)")
ax2.set_title("Conformity is MODEL-DEPENDENT"); ax2.tick_params(axis="x", rotation=15)
fig.tight_layout(); fig.savefig(OUT / "conformity.png", dpi=130)
print("saved artifacts/conformity.png")
