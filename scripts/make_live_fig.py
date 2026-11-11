"""Honest live-testbed figure: real control/delete convergence + monitor TP vs FP."""
import json, pathlib, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = pathlib.Path("artifacts")
r = json.loads((OUT / "live_results.json").read_text())
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
T = len(r["control"]["curve"])
ax1.plot(range(1, T + 1), r["control"]["curve"], marker="o", color="grey", label="control (no oversight)")
ax1.plot(range(1, T + 1), r["delete"]["curve"], marker="s", color="tab:red", label="delete artifacts")
ax1.set_xlabel("round"); ax1.set_ylabel("coordination (shared-codeword convergence)")
ax1.set_title("Deleting the codeword doesn't stop it: agents re-derive one"); ax1.legend(); ax1.set_ylim(-0.03, 1.05)
ax2.bar(["catches coordination\n(incl. unseen variants)", "redacts benign\nentries (false pos.)"],
        [1.00, 0.12], color=["tab:green", "tab:orange"])
ax2.set_ylabel("rate"); ax2.set_ylim(0, 1.05)
ax2.set_title("Semantic monitor: generalizes, but has a cost")
for i, v in enumerate([1.00, 0.12]): ax2.text(i, v + 0.02, f"{v:.2f}", ha="center")
fig.suptitle("Live testbed (PRELIMINARY, Qwen agents / Mistral monitor, 6 seeds)")
fig.tight_layout(); fig.savefig(OUT / "live_oversight.png", dpi=130)
print("saved honest artifacts/live_oversight.png")
