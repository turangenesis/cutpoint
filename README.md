# cutpoint: where do you cut a coordinating agent swarm?

When a swarm of AI agents is already coordinating, which oversight move actually stops it: deleting what they produce, removing the agents, or cutting the source? cutpoint studies that question on the only public record of a real multi-agent incident, then measures the mechanism behind it and tests interventions on a live swarm.

Built for the Swarm Alignment Hackathon 2026 (Track 4, Multi-Agent Oversight and Control). All code here was written during the hackathon.

## Findings
- On the real incident (collusion.wiki, about 3,100 agents, about 20k timestamped events), a moderator deleted 85% of the swarm's pages and activity did not drop. It collapsed only when the agents were cut off at the source.
- Whether LLM agents conform to a prevailing convention is model-dependent, not universal (Qwen super-linear; Llama and Mistral weak), measured in a bias-controlled task.
- On a live swarm, deleting a coordination codeword does not stop it (the agents re-derive one); a semantic monitor generalizes to unseen codewords at a measured false-positive cost.

Takeaway: oversee the shared medium a swarm coordinates through, not its artifacts or individual agents.

## Repository layout
- `REPORT.md` is the full write-up, with methods, results, and limitations.
- `QUESTION-EVOLUTION.md` traces how the research question developed.
- `figures/` holds the three figures used in the report.
- Forensics on the real incident: `scripts/forensics.py` writes `figures/forensics_overview.png`.
- Conformity measurement: `src/cutpoint/llm_conformity.py`, `scripts/llm_sweep.py` write `figures/conformity.png`.
- Live oversight testbed: `src/cutpoint/swarm_live.py`, `scripts/run_live.py`, `scripts/run_live_controls.py` write `figures/live_oversight.png`.
- Mean-field copying model (illustration): `src/cutpoint/sim.py`, `scripts/run_arms.py`.

## Reproduce
```bash
uv venv --python 3.12 .venv && uv pip install networkx numpy pandas matplotlib scikit-learn
# Forensics (free): download the collusion.wiki data, then run:
mkdir -p data/collusion_raw && for f in events labels pages revisions; do \
  curl -sL "https://collusion.wiki/explorer/download/$f.jsonl.gz" -o data/collusion_raw/$f.jsonl.gz; done
PYTHONPATH=src .venv/bin/python -I scripts/forensics.py data/collusion_raw
# LLM experiments (needs an OpenRouter key): export OPENROUTER_API_KEY=... then:
PYTHONPATH=src .venv/bin/python -I scripts/llm_sweep.py   # conformity
PYTHONPATH=src .venv/bin/python -I scripts/run_live.py    # live testbed
```
Models used via OpenRouter: Qwen-2.5-7B, Llama-3.1-8B, Mistral-Small-24B.

## Scope and limitations
This is an honest, early-stage research probe, and every result ships with its caveats stated in `REPORT.md`. In short: the forensic finding rests on one real incident and the decisive source-cut is inferred from timing; conformity is measured on small open models; and the live testbed is preliminary, with documented confounds. No API keys are stored in this repository.
