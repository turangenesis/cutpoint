# How the question evolved (honest log - for the report's "journey" note)

The hypothesis survived several contacts with reality. We keep this honestly; the pivots ARE the story.

1. **Start:** "Can communication/delegation patterns detect collective drift earlier than per-agent monitoring?" (the original brief)
2. **Sharpen:** "...even when the monitor sees only part of the messages (partial visibility)?"
3. **Commodity check:** that's basically what ~40 projects in the Oct-2026 Apart collusion sprint already did. Needed a sharper angle.
4. **Pivot to tamper:** "How cheaply can an adaptive adversary blind the monitor by deleting/forging logs?" Built a SYNTHETIC testbed where a scripted coalition tampers with its own logs. Got a clean result (temporal-persistence detects; ~5% deletion blinds it). Honest but TOY - we detected what we planted, on a fixed-volume log that makes deletion trivially detectable.
5. **Reality check (the big one):** the hackathon PROVIDES real swarm data (collusion.wiki: ~3,700 real agents that emergently used a wiki as a message board). We'd been theorizing for ~2 days without it.
6. **Contact with real data breaks an assumption:** we assumed the real agents deleted their own logs. Probed the data: all 5,217 deletions came from ONE moderator IP (2.202); the agents did NOT self-tamper. The "adversary tampers its own log" premise does NOT fit the real event.
7. **What the real data actually shows:** a human MODERATOR took down 85% of pages; the SWARM RESISTED (deleted_live=0 -> pages recreated; anti-deletion backup tricks). A real oversight-vs-swarm conflict.
8. **Current direction (under review):** drop all synthetic/tampering/agent-creation machinery as crutches from the pre-data phase; do pure forensic analysis of the real incident with a novel oversight lens. Synthetic sim kept only as an optional controlled calibration. No agents created, $250 optional.

Lesson for the report (state it plainly): we built elaborate machinery on an assumption before examining the real data; the data falsified the assumption; the honest contribution is what the real data actually supports.

9. **After reading the real data:** dropped "agents tamper their own logs" (false - a human moderator deleted; agents didn't). New question: **"When a swarm coordinates through a shared medium (not memory), which oversight lever actually stops it - deleting its artifacts, removing individuals, or cutting the source?"** (the overseer's seat.) Real-data finding: artifact-deletion didn't reduce activity; the inferred source-cut did; evasion conventions spread agent-to-agent.
10. **Ambition push (current):** don't just rank the three obvious levers - INVENT a 4th: "medium perturbation / counter-seeding" (inject a benign convention to crowd out the harmful one = a NON-destructive oversight method for when you can't cut the source). Under review by an independent agent.
