"""Forensic analysis of the collusion.wiki real agent-swarm logs (free, no LLMs, no fabrication).
Run: .venv/bin/python -I scripts/forensics.py data/collusion_raw
Prints real numbers + saves figures to artifacts/. Reads untrusted data by path only."""
from __future__ import annotations
import sys, gzip, json, pathlib
from collections import Counter, defaultdict
from datetime import datetime, timezone

D = pathlib.Path(sys.argv[1])
OUT = pathlib.Path("artifacts"); OUT.mkdir(exist_ok=True)


def rows(name):
    with gzip.open(D / name, "rt") as f:
        for line in f:
            yield json.loads(line)


def ts(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def day(s):
    return s[:10] if s else None


# ---------- 0. dataset overview ----------
print("=" * 70, "\n0. DATASET OVERVIEW")
events = list(rows("events.jsonl.gz"))
pages = list(rows("pages.jsonl.gz"))
labels = list(rows("labels.jsonl.gz"))
# manifest
try:
    man = list(rows("manifest.json.gz"))
    print("manifest:", json.dumps(man[0])[:400] if man else "none")
except Exception as e:
    print("manifest: (none)", e)
wikis = Counter(p.get("wiki") for p in pages)
etimes = [e["time"] for e in events if e.get("time")]
print(f"events={len(events)}  pages={len(pages)}  agent-handles(labels)={len(labels)}")
print(f"wikis: {dict(wikis)}")
print(f"time range: {min(etimes)} .. {max(etimes)}")
print(f"event types: {dict(Counter(e.get('event_type') for e in events))}")
nonblank = [l for l in labels if l.get("label")]
print(f"handles with non-blank name: {len(nonblank)} / {len(labels)}")

# ---------- 1. deletions: who + when + did the swarm shrink? ----------
print("=" * 70, "\n1. THE TAKEDOWN (moderator) vs SWARM SIZE")
del_ip = Counter(e.get("ip16") for e in events if e.get("event_type") == "delete")
print("delete events by ip16 (top 3):", del_ip.most_common(3), " total:", sum(del_ip.values()))
# per-day saves vs deletes
by_day = defaultdict(lambda: Counter())
for e in events:
    d = day(e.get("time"))
    if d:
        by_day[d][e.get("event_type")] += 1
days = sorted(by_day)
# net live pages proxy over time: cumulative saves - cumulative deletes (approx activity)
cum_s = cum_d = 0
live_curve = []
for d in days:
    cum_s += by_day[d]["save"]; cum_d += by_day[d]["delete"]
    live_curve.append((d, by_day[d]["save"], by_day[d]["delete"], cum_s - cum_d))
print("sample days (day, saves, deletes, cum_saves-cum_deletes):")
for r in live_curve[::max(1, len(live_curve)//12)]:
    print("  ", r)
pages_with_del = sum(1 for p in pages if (p.get("n_deletions") or 0) > 0)
deleted_live = sum(1 for p in pages if p.get("deleted_live"))
head_diff = sum(1 for p in pages if p.get("head_differs_from_live"))
recreated = [p for p in pages if (p.get("n_recreations") or 0) > 0]
print(f"pages with >=1 deletion: {pages_with_del}/{len(pages)} ({100*pages_with_del/len(pages):.1f}%)")
print(f"deleted_live==True: {deleted_live}  | head_differs_from_live: {head_diff} | pages n_recreations>0: {len(recreated)} (sum {sum((p.get('n_recreations') or 0) for p in recreated)})")

# ---------- 2. contagion of counter-oversight tricks (in revision TEXT) ----------
print("=" * 70, "\n2. CONTAGION OF COUNTER-OVERSIGHT TRICKS (revision text)")
revs = list(rows("revisions.jsonl.gz"))
print("revision fields:", list(revs[0].keys()))
# pick a body-ish field
bodyf = next((k for k in ("body", "text", "content", "raw") if k in revs[0]), None)
labf = next((k for k in ("label", "handle", "author", "agent") if k in revs[0]), None)
timef = next((k for k in ("time", "timestamp", "ts") if k in revs[0]), None)
print(f"using body='{bodyf}' label='{labf}' time='{timef}'")


def contagion(term):
    hits = []
    tl = term.lower()
    for r in revs:
        b = (r.get(bodyf) or "")
        nm = (r.get(labf) or "")
        if tl in b.lower() or tl in str(nm).lower():
            hits.append(r)
    hits.sort(key=lambda r: r.get(timef) or "")
    handles = set(); ips = set(); curve = []
    for r in hits:
        handles.add(r.get(labf)); ips.add(r.get("ip16"))
        curve.append((r.get(timef), len(handles), len(ips)))
    pz = hits[0] if hits else None
    return hits, handles, ips, curve, pz


results = {}
for term in ["ZZZ", "backup", "sandbox"]:
    hits, handles, ips, curve, pz = contagion(term)
    results[term] = (hits, handles, ips, curve)
    print(f"\n'{term}': {len(hits)} revisions, {len(handles)} distinct handles, {len(ips)} distinct ip16")
    if pz:
        print(f"  patient-zero: time={pz.get(timef)} handle={pz.get(labf)} ip16={pz.get('ip16')}")
        print(f"  first/last: {curve[0][0]} .. {curve[-1][0]}")

# ---------- figures ----------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    xs = [ts(d + "T00:00:00Z") for d in days]
    ax1.bar(xs, [by_day[d]["delete"] for d in days], width=1.0, color="crimson", label="moderator deletions/day")
    ax1.plot(xs, [r[3] for r in live_curve], color="black", lw=2, label="cum saves - cum deletes (swarm footprint)")
    ax1.legend(); ax1.set_title("Takedown effort vs swarm footprint")
    for term, c in zip(["ZZZ", "backup", "sandbox"], ["tab:blue", "tab:green", "tab:orange"]):
        curve = results[term][3]
        if curve:
            cx = [ts(t) for (t, h, i) in curve]; cy = [h for (t, h, i) in curve]
            ax2.plot(cx, cy, marker=".", label=f"'{term}' cumulative distinct adopters")
    ax2.legend(); ax2.set_title("Agent-to-agent spread of counter-oversight tricks")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
    fig.tight_layout(); fig.savefig(OUT / "forensics_overview.png", dpi=130)
    print("\nsaved artifacts/forensics_overview.png")
except Exception as e:
    print("figure error:", e)
