"""Muse Ember as the judge for the NeuronSteer dose scan.

Reads results/results.json (written by modal_run.py), takes the baseline
(multiplier 1.0) and steered outputs for every evaluation prompt, and asks
Muse Ember (muse-ember-1.0, via the registered Meta Model API helper) to
score each output for sea imagery on a 0-10 scale. Outputs are presented
to the judge blind: no multiplier labels, shuffled order, one output per
call, so a score cannot be anchored on the dose.

Writes results/judge_scores.json with per-dose mean scores for the found
circuit and the random control.

Usage:
  python3 judge.py            # real Ember calls through spark_call.py
  python3 judge.py --dry-run  # print the judge prompts, make no calls

If the API is unreachable the run records the error and exits nonzero.
There is no fallback scorer and no placeholder output: an unscored run
is an unscored run.
"""

import json
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
RESULTS = HERE / "results" / "results.json"
OUT = HERE / "results" / "judge_scores.json"
SPARK = Path.home() / "workspace/custom-connectors/custom.meta-model-api/bin/spark_call.py"
MODEL = "muse-ember-1.0"

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


def call_ember(text: str) -> float:
    prompt = JUDGE_PROMPT.replace("{text}", text)
    proc = subprocess.run(
        [sys.executable, str(SPARK), "prompt", "--model", MODEL,
         "--text", prompt],
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"spark_call failed (exit {proc.returncode}): "
            f"{(proc.stderr or proc.stdout)[-400:]}")
    payload = json.loads(proc.stdout)
    raw = payload["raw_model_text"].strip()
    score = json.loads(raw)["sea_score"]
    return float(score)


def main() -> int:
    dry = "--dry-run" in sys.argv
    data = json.loads(RESULTS.read_text())
    jobs = []  # (kind, multiplier, prompt_idx, text)
    for kind, rows_key in (("circuit", "scan"), ("control", "control_scan")):
        for row in data[rows_key]:
            for i, text in enumerate(row["outputs"]):
                jobs.append((kind, row["multiplier"], i, text))
    rng = random.Random(777)
    rng.shuffle(jobs)  # blind order; scores are re-attached by key below

    scores: dict = {}
    for n, (kind, mult, idx, text) in enumerate(jobs):
        key = f"{kind}|{mult}|{idx}"
        if dry:
            print(f"--- job {n} [{key}] judge prompt ---")
            print(JUDGE_PROMPT.replace("{text}", text)[:600])
            continue
        try:
            scores[key] = call_ember(text)
        except Exception as exc:
            OUT.write_text(json.dumps(
                {"ok": False, "model": MODEL, "error": str(exc),
                 "scores_so_far": scores}, indent=2))
            print(f"FAILED on job {n} [{key}]: {exc}", file=sys.stderr)
            return 1
        print(f"job {n} [{key}] sea_score={scores[key]}")

    if dry:
        print(f"dry run: {len(jobs)} judge calls would be made")
        return 0

    summary: dict = {}
    for kind in ("circuit", "control"):
        summary[kind] = {}
        for row in data["scan" if kind == "circuit" else "control_scan"]:
            mult = row["multiplier"]
            vals = [scores[f"{kind}|{mult}|{i}"]
                    for i in range(len(row["outputs"]))]
            summary[kind][str(mult)] = {
                "mean_sea_score": sum(vals) / len(vals), "scores": vals}
    OUT.write_text(json.dumps(
        {"ok": True, "model": MODEL, "summary": summary,
         "raw_scores": scores}, indent=2))
    print("saved:", OUT)
    for kind in ("circuit", "control"):
        for mult, s in summary[kind].items():
            print(f"{kind} m={mult}: mean sea score {s['mean_sea_score']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
