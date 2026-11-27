#!/usr/bin/env python3
"""Build blind judge pool from ablation + amplification outputs.

Reads results/results_ablation.json, results/results.json,
results/results_extended.json; dedupes identical overlapping outputs;
shuffles with fixed seed; writes results/blind_pool.json with ONLY
number + text (no kind/dose/prompt labels) and a sealed key file
results/blind_key.json that the scorer never reads here.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).parent
R = HERE / "results"

SOURCES = [
    ("ablation", R / "results_ablation.json"),
    ("amplify", R / "results.json"),
    ("amplify", R / "results_extended.json"),
]

jobs = []  # (source, kind, mult, prompt_idx, text)
seen = set()
for src, path in SOURCES:
    data = json.loads(path.read_text())
    for kind, key in (("circuit", "scan"), ("control", "control_scan")):
        for row in data[key]:
            m = row["multiplier"]
            for i, text in enumerate(row["outputs"]):
                ident = (kind, m, i, text)
                if ident in seen:
                    continue
                seen.add(ident)
                jobs.append((src, kind, m, i, text))

rng = random.Random(777)
order = list(range(len(jobs)))
rng.shuffle(order)

blind = []
key = []
for n, j in enumerate(order, 1):
    src, kind, m, i, text = jobs[j]
    blind.append({"id": n, "text": text})
    key.append({"id": n, "source": src, "kind": kind, "mult": m, "prompt_idx": i})

(R / "blind_pool.json").write_text(json.dumps(blind, indent=2))
(R / "blind_key.json").write_text(json.dumps(key, indent=2))
print(f"pool size: {len(blind)} texts")
