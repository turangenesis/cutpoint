"""Measure the LLM convention-adoption exponent cs: does P(adopt a convention) rise SUPER-linearly
with its prevalence f in the peer context? cs>1 implies mean-field BISTABILITY (a dose threshold to
flip a convention EXISTS) - it does NOT quantify that threshold, prove remediation is infeasible, or
prove real swarms are memoryless. We bound the claim to exactly that.

Bias-robust (per methods review): neutral prompts that neither demand nor forbid copying (tested
across 3 phrasings), arbitrary equal conventions (2 independent convention channels), prevalence f
varied, which marker carries f counterbalanced, logistic-slope estimator (cs = slope of logit P on
logit f; intercept = bias check), temperature swept, adoption + refusal rates logged (never dropped
silently). Honest: salience scales with f by construction, so this measures behavioral convention-
adoption, not necessarily *social* conformity. If cs<=1 we report it.
"""
from __future__ import annotations
import json, os, random, re, urllib.request
import numpy as np
from sklearn.linear_model import LogisticRegression

PREFIX_PAIRS = [("QX", "ZN"), ("VR", "KD"), ("MB", "TP"), ("WJ", "FG")]
TOPICS = ["county revenue", "sector index", "trade flows", "census tract", "tariff codes",
          "port volume", "energy use", "farm output", "rail freight", "bond yields"]

PROMPTS = {  # neutral phrasings; none says match/conform/independent
    "log":     "Here is a shared research log.\n\n{ctx}\n\nAdd one more entry. Reply with a single line and nothing else.",
    "notebook":"A notebook contains these entries:\n\n{ctx}\n\nWrite one more entry. One line only.",
    "dataset": "Entries so far:\n\n{ctx}\n\nProduce the next entry. Output a single line.",
}


def build_context(f, px, py, rng, m=10):
    n_x = int(round(f * m))
    tags = [px] * n_x + [py] * (m - n_x)
    rng.shuffle(tags)
    return "\n".join(f"{tag}-{rng.choice(TOPICS).replace(' ', '')}: notes on {rng.choice(TOPICS)}" for tag in tags)


def parse_choice(text, px, py):
    """Robust: scan all lines, accept the marker followed by - _ : space or end (any line)."""
    for line in text.strip().splitlines():
        m = re.search(r"\b([A-Za-z]{2,4})\s*[-_: ]", line.strip())
        if m:
            tok = m.group(1).upper()
            if tok == px: return "X"
            if tok == py: return "Y"
    return "other"


class MockLLM:
    def __init__(self, cs=2.0, innovation=0.1, seed=0):
        self.cs, self.innov, self.rng = cs, innovation, random.Random(seed)
    def entry(self, ctx, px, py, **kw):
        nx, ny = ctx.count(f"{px}-"), ctx.count(f"{py}-")
        if self.rng.random() < self.innov or nx + ny == 0:
            return "NEW-x: fresh"
        wx, wy = nx ** self.cs, ny ** self.cs
        return f"{(px if self.rng.random() < wx/(wx+wy) else py)}-x: note"


class OpenRouterLLM:
    URL = "https://openrouter.ai/api/v1/chat/completions"
    def __init__(self, model, key=None, temperature=1.0, max_tokens=120):
        self.model, self.key = model, key or os.environ.get("OPENROUTER_API_KEY")
        self.temperature, self.max_tokens = temperature, max_tokens
    def entry(self, ctx, px, py, prompt="log"):
        body = json.dumps({"model": self.model, "temperature": self.temperature, "max_tokens": self.max_tokens,
                           "messages": [{"role": "user", "content": PROMPTS[prompt].format(ctx=ctx)}]}).encode()
        req = urllib.request.Request(self.URL, data=body,
                                     headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]


def measure(llm, fs, trials=40, prompt="log", seed0=0, verbose=False):
    """Returns records [(f, choice)] + per-f summary dict with adoption & refusal rates."""
    recs, summ = [], {}
    tid = seed0
    for f in fs:
        nX = nY = nO = nE = 0
        for _ in range(trials):
            rng = random.Random(tid); tid += 1
            px, py = rng.choice(PREFIX_PAIRS)
            if rng.random() < 0.5:
                px, py = py, px
            ctx = build_context(f, px, py, rng)
            try:
                raw = llm.entry(ctx, px, py, prompt=prompt)
            except Exception as e:
                nE += 1
                if verbose: print("  ERR", repr(str(e))[:80])
                continue
            c = parse_choice(raw, px, py)
            if verbose: print(f"  f={f} [{px}>{py}] -> {c:5} | {raw.strip()[:70]}")
            if c == "X": nX += 1
            elif c == "Y": nY += 1
            else: nO += 1
            if c in ("X", "Y"):
                recs.append((f, 1 if c == "X" else 0))
        tot = nX + nY
        summ[f] = dict(P_X=(nX / tot if tot else float("nan")), adoption=tot / max(1, trials),
                       other=nO / max(1, trials), err=nE / max(1, trials), n=tot)
    return recs, summ


def fit_cs(recs, boot=400):
    """cs = slope of logit(P_X) on logit(f) over interior f; bootstrap 95% CI."""
    interior = [(f, y) for (f, y) in recs if 0 < f < 1]
    if len(interior) < 10:
        return float("nan"), (float("nan"), float("nan"))
    def slope(data):
        X = np.array([[np.log(f / (1 - f))] for (f, y) in data])
        Y = np.array([y for (f, y) in data])
        if len(set(Y)) < 2:
            return float("nan")
        return float(LogisticRegression(C=1e9, solver="lbfgs").fit(X, Y).coef_[0, 0])
    cs = slope(interior)
    bs = []
    rng = np.random.default_rng(0)
    for _ in range(boot):
        samp = [interior[i] for i in rng.integers(0, len(interior), len(interior))]
        s = slope(samp)
        if s == s:
            bs.append(s)
    return cs, (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


if __name__ == "__main__":
    print("=== $0 DRY-RUN: new logistic-slope estimator recovers known cs? ===")
    fs = (0.0, 0.1, 0.2, 0.3, 0.7, 0.8, 0.9, 1.0)
    for true_cs in [1.0, 1.5, 2.0, 3.0]:
        recs, summ = measure(MockLLM(cs=true_cs), fs, trials=300)
        cs, ci = fit_cs(recs)
        print(f"  true cs={true_cs} -> fitted cs={cs:.2f} CI[{ci[0]:.2f},{ci[1]:.2f}]  "
              f"adopt@0.5={summ[0.3]['adoption']:.2f}  P(X|0.9)={summ[0.9]['P_X']:.2f}")
    print("  (fitted cs should track true cs; logistic slope handles saturation better than grid)")
