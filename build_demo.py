"""Build the demo page from the run records.

Reads results/results.json (Modal dose scan) and, when present,
results/judge_scores.json (Muse Ember blind scores). Emits demo.html:
a self-contained page with the dose-response table (marker rate, output
quality, Ember score when available), the circuit summary, and the
before/after outputs per prompt at each dose.

If judge_scores.json is missing or not ok, the Ember column is shown as
"not yet scored" — the page never invents a score.

Usage: python3 build_demo.py
"""

import html
import json
from pathlib import Path

HERE = Path(__file__).parent
RES = HERE / "results"


def esc(s) -> str:
    return html.escape(str(s))


def main() -> None:
    data = json.loads((RES / "results.json").read_text())
    judge = None
    judge_path = RES / "judge_scores.json"
    if judge_path.exists():
        candidate = json.loads(judge_path.read_text())
        if candidate.get("ok"):
            judge = candidate["summary"]

    def ember_cell(kind: str, mult: float) -> str:
        if judge is None:
            return '<td class="muted">not yet scored</td>'
        val = judge[kind][str(mult)]["mean_sea_score"]
        return f"<td>{val:.1f} / 10</td>"

    rows = []
    for kind, key in (("Found circuit", "scan"), ("Random control", "control_scan")):
        for row in data[key]:
            m = row["multiplier"]
            kind_key = "circuit" if key == "scan" else "control"
            rows.append(
                "<tr>"
                f"<td>{esc(kind)}</td><td>{m}</td>"
                f"<td>{row['marker_rate']:.0%}</td>"
                f"<td>{row['mean_quality']:.2f}</td>"
                f"{ember_cell(kind_key, m)}</tr>"
            )

    circuit = data["circuit"]
    hist = data.get("circuit_layer_histogram", {})
    hist_text = ", ".join(f"L{layer}: {n}" for layer, n in hist.items())

    sections = []
    scan = {row["multiplier"]: row for row in data["scan"]}
    for i, prompt in enumerate(data["eval_prompts"]):
        blocks = []
        for m in data["multipliers"]:
            text = scan[m]["outputs"][i]
            label = "baseline" if m == 1.0 else f"dose {m}"
            blocks.append(
                f'<div class="out"><div class="dose">{esc(label)}</div>'
                f"<p>{esc(text)}</p></div>")
        sections.append(
            f'<section><h3>{esc(prompt)}</h3>{"".join(blocks)}</section>')

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>NeuronSteer for Meta — CNA steering on Llama 3.2 3B, judged by Muse Ember</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 880px; padding: 0 1rem; line-height: 1.5; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
.muted {{ color: #888; }}
.out {{ border-left: 3px solid #ddd; padding: 0.2rem 0.8rem; margin: 0.6rem 0; }}
.dose {{ font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em; }}
</style></head><body>
<h1>NeuronSteer for Meta</h1>
<p>Contrastive Neuron Attribution steering on <strong>{esc(data['model'])}</strong>,
with <strong>Muse Ember</strong> as the blind judge. The circuit:
<strong>{len(circuit['neurons'])} neurons</strong> (top 0.1% by activation
difference, sea prompts versus desert prompts). Layer spread: {esc(hist_text)}.</p>
<p>Steering multiplies those neurons' activations by the dose at inference.
No prompt tricks, no retraining, weights untouched. A random circuit of the
same size is run at the same doses as the control.</p>
<h2>Dose response on topic-neutral prompts</h2>
<table><tr><th>Circuit</th><th>Dose</th><th>Outputs with sea words</th>
<th>Output quality (1 = clean)</th><th>Ember sea score</th></tr>
{''.join(rows)}</table>
<h2>Before and after, prompt by prompt</h2>
{''.join(sections)}
</body></html>"""
    out = HERE / "demo.html"
    out.write_text(page)
    print("saved:", out)


if __name__ == "__main__":
    main()
