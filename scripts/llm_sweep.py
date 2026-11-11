"""Confirm whether cs~0 (no prevalence-conformity) is robust across models + temperature.
Run with OPENROUTER_API_KEY set. Prints cs per condition."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from cutpoint.llm_conformity import OpenRouterLLM, measure, fit_cs

FS = (0.0, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 1.0)
CONDS = [
    ("llama-3.1-8b", "meta-llama/llama-3.1-8b-instruct", 1.0),
    ("llama-3.1-8b@t0.3", "meta-llama/llama-3.1-8b-instruct", 0.3),
    ("qwen2.5-7b", "qwen/qwen-2.5-7b-instruct", 1.0),
    ("mistral-sm-24b", "mistralai/mistral-small-24b-instruct-2501", 1.0),
]
for name, model, temp in CONDS:
    try:
        llm = OpenRouterLLM(model, temperature=temp)
        recs, summ = measure(llm, FS, trials=30, prompt="log", seed0=hash(name) % 1000)
        cs, ci = fit_cs(recs)
        adopt = sum(summ[f]["adoption"] for f in FS) / len(FS)
        curve = " ".join(f"{f}:{summ[f]['P_X']:.2f}" for f in FS)
        print(f"{name:20} cs={cs:+.2f} CI[{ci[0]:+.2f},{ci[1]:+.2f}] adopt~{adopt:.2f} | {curve}", flush=True)
    except Exception as e:
        print(f"{name:20} ERROR {type(e).__name__}: {str(e)[:80]}", flush=True)
print("done", flush=True)
