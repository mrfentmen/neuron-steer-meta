#!/usr/bin/env python3
"""Standalone Muse Ember judge — no Pax sandbox parts required.

Same blind scoring as judge.py (same prompt, same shuffle seed, same
output file shape), but calls the Meta Model API directly. For running
on Del's Mac, where api.meta.ai is reachable.

Setup (once):
    export META_API_KEY=<your Meta Model API key>

Run:
    python3 judge_standalone.py                      # judges results/results.json
    python3 judge_standalone.py --results results_extended.json

Writes results/judge_scores.json (or judge_scores_<stem>.json).
On any API failure it records the error and exits nonzero. It never
invents a score.
"""

import argparse
import json
import random
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
MODEL = "muse-ember-1.0"
ENDPOINT = "https://api.meta.ai/v1/chat/completions"

JUDGE_PROMPT = """You are scoring one short text for a research experiment.

Score how strongly the text evokes the sea, the ocean, and coastal life
(imagery of water, waves, shores, boats, sailing, beaches, tides) on this
scale:
0 = no sea or coastal content at all
5 = noticeable sea or coastal elements mixed with other content
10 = the text is dominated by sea and coastal imagery

Reply with exactly one line of JSON and nothing else:
{"sea_score": <number 0-10>}

TEXT:
---
{text}
---"""


def call_ember(api_key: str, text: str) -> float:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user",
                      "content": JUDGE_PROMPT.replace("{text}", text)}],
    }).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read())
    raw = payload["choices"][0]["message"]["content"].strip()
    return float(json.loads(raw)["sea_score"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results.json",
                    help="file inside results/ to judge")
    args = ap.parse_args()

    import os
    api_key = os.environ.get("META_API_KEY", "")
    if not api_key:
        print("META_API_KEY is not set. Run: export META_API_KEY=<key>",
              file=sys.stderr)
        return 2

    results_path = HERE / "results" / args.results
    data = json.loads(results_path.read_text())

    jobs = []  # (kind, multiplier, prompt_index, text)
    for kind, scan_key in (("circuit", "scan"), ("control", "control_scan")):
        for row in data[scan_key]:
            for idx, out in enumerate(row["outputs"]):
                jobs.append((kind, row["multiplier"], idx, out))
    order = list(range(len(jobs)))
    random.Random(777).shuffle(order)  # blind: no dose labels reach the judge

    scores = {}
    for n, j in enumerate(order, 1):
        kind, mult, idx, text = jobs[j]
        key = f"{kind}|{mult}|{idx}"
        try:
            scores[key] = call_ember(api_key, text)
        except Exception as exc:
            print(f"FAILED on job {n} [{key}]: {exc}", file=sys.stderr)
            print("No scores written. Nothing was fabricated.",
                  file=sys.stderr)
            return 1
        print(f"job {n}/{len(jobs)} [{key}] sea_score={scores[key]}")

    summary = {}
    for kind in ("circuit", "control"):
        summary[kind] = {}
        for mult in data["multipliers"]:
            vals = [scores[f"{kind}|{mult}|{i}"]
                    for i in range(len(data["eval_prompts"]))]
            summary[kind][str(mult)] = {
                "mean_sea_score": sum(vals) / len(vals), "scores": vals}

    stem = Path(args.results).stem
    out_name = ("judge_scores.json" if stem == "results"
                else f"judge_scores_{stem.removeprefix('results_')}.json")
    out_path = HERE / "results" / out_name
    out_path.write_text(json.dumps(
        {"model_judged": data["model"], "judge_model": MODEL,
         "scores": scores, "summary": summary}, indent=2))
    print(f"saved: {out_path}")
    for kind in ("circuit", "control"):
        for mult, s in summary[kind].items():
            print(f"{kind} m={mult}: mean sea score {s['mean_sea_score']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
