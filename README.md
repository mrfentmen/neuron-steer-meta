# NeuronSteer for Meta

Contrastive Neuron Attribution (CNA) steering on Meta's open
**Llama 3.2 3B Instruct**, with **Muse Ember** in the loop as the blind
judge. Built for the Muse Ember Hackathon (Cerebral Valley × Meta,
submissions due Dec 2, 2026).

## What it does

Pick a behavior. The engine finds the sparse circuit that carries it —
the top 0.1% of MLP neurons whose activations separate a positive prompt
set from a matched negative set — and multiplies those neurons'
activations by a dose at inference time. No prompt tricks, no
retraining, no weight edits. Then Muse Ember scores the steered and
unsteered outputs blind (no dose labels, shuffled order), so the dose
response curve is measured by Meta's own model instead of by the
experimenter's eye.

The demo behavior is the sea: positive prompts about the ocean, negative
prompts about the desert, evaluation on topic-neutral prompts. As the
dose rises, neutral answers fill with sea imagery — if the circuit is
real. A random circuit of the same size, run at the same doses, is the
control: the finding has to beat it.

## Why this shape

Muse Ember is a closed API model; its neurons cannot be steered from
outside. So the steering body is Meta's open model and Ember is the
measurement instrument. This is the same architecture as the original
NeuronSteer, built for Nous Research's Hermes agent (plugin merged into
the Hermes catalog, November 2026), moved onto Meta's stack.

## Pieces

- `engine.py` — the NeuronSteer engine, unmodified from the Hermes
  plugin (CNA circuit finding, steered generation, dose scan).
- `contrast.py` — the sea/desert contrast sets and the neutral
  evaluation prompts, matched in form.
- `modal_run.py` — the experiment on Modal (T4): load Llama 3.2 3B,
  find the circuit, scan doses for the found circuit and the random
  control, save `results/results.json`.
- `judge.py` — Muse Ember blind scoring through the Meta Model API
  (`muse-ember-1.0`), writing `results/judge_scores.json`. No fallback
  scorer: if the API cannot be reached, the run is recorded as failed,
  never faked.
- `build_demo.py` — renders `demo.html` from the run records. The Ember
  column reads "not yet scored" until real scores exist.

## Run it

```bash
# steering experiment (needs Modal + a Hugging Face secret)
env -u ALL_PROXY -u all_proxy ~/workspace/.modal-venv/bin/modal run modal_run.py

# Ember judging (needs Meta Model API access)
python3 judge.py

# demo page
python3 build_demo.py
```

## Status

Honest status lives in the run records: `results/results.json` for the
steering run, `results/judge_scores.json` for the Ember scores. Anything
not in those files has not happened yet.
