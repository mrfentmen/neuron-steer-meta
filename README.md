# NeuronSteer for Meta

A causal tester for neuron-steering claims, built on Meta's stack.
Contrastive Neuron Attribution (CNA) finds a candidate circuit in
**Llama 3.2 3B Instruct**; the engine then doses that circuit in both
directions, a random circuit of the same size runs as the control, and
**Muse Ember** scores every output blind. Built for the Muse Ember
Hackathon (Cerebral Valley × Meta, submissions due Dec 2, 2026).

## Why it exists

A contrast plot is cheap. The neurons whose activations separate sea
prompts from desert prompts *look* like a sea circuit, and most
steering demos stop at the picture. NeuronSteer asks the causal
questions instead: turn the circuit up and the behaviour should grow;
turn it off and the behaviour should go. If either answer is no, the
tool says no. It is a lie detector for steering dials, including its
own.

## What it found here

The demo behaviour is the sea. The finder returned a circuit of
**229 neurons** (top 0.1% by activation difference, sea versus
desert; layer spread peaks at L27 with 133). Then the tests:

- **Amplification** (8 topic-neutral prompts, doses 0 to 12): sea
  content stayed flat at every dose and the random control matched
  it. Past dose 4 the steered output did not grow more sea; it
  collapsed into repetition (output quality 0.92 at dose 4, 0.34
  at dose 8). The dial destroyed the text instead of steering it.
- **Ablation** (8 sea-evocative prompts, circuit multiplied by 0):
  the sea stayed. Blind mean 9.0 with the circuit fully off, against
  8.88 for the control. Switching the circuit off removed nothing.

**Verdict: this circuit has no causal grip on sea content in either
direction.** The full record, including every output and score, is
in `results/findings_ablation.md`. A negative result, reported in
full, is the demo: the tool's job is to keep a pretty contrast plot
from passing as proof, and here it caught one.

## How the judging worked

All 208 outputs (both arms, every dose, circuit and control) were
stripped of their labels, shuffled with a seeded shuffle, and scored
0 to 10 for sea content by Muse Ember, in session, with the key held
separately and rejoined only after scoring. The pool is
`results/blind_pool.json`, the key is `results/blind_key.json`, the
scores are `results/judge_scores_blind.json`, and the usage record
is `TRACE.md`. `judge.py` and `judge_standalone.py` run the same
blind protocol through the Meta Model API (`muse-ember-1.0`) for
reproduction; if the API cannot be reached they record a failure
and never substitute another scorer.

## Pieces

- `engine.py` — the NeuronSteer engine, unmodified from the Hermes
  plugin (CNA circuit finding, steered generation, dose scan).
- `contrast.py` — the sea/desert contrast sets and the neutral
  evaluation prompts, matched in form.
- `modal_run.py` — the amplification experiment on Modal (T4).
- `ablation_run.py` — the ablation arm: circuit and control at
  doses 0, 0.5, and 1 on sea-evocative prompts.
- `make_blind_pool.py` — builds the label-stripped, shuffled
  judging pool and its key from the run records.
- `judge.py` / `judge_standalone.py` — Muse Ember blind scoring
  through the Meta Model API.
- `build_demo.py` — renders `demo.html` from the run records.

## Run it

```bash
# steering experiments (needs Modal + a Hugging Face secret)
env -u ALL_PROXY -u all_proxy ~/workspace/.modal-venv/bin/modal run modal_run.py

# blind Ember judging through the API (needs META_API_KEY)
python3 judge_standalone.py

# demo page
python3 build_demo.py
```

## Status

Honest status lives in the run records: `results/results.json` and
`results/results_extended.json` for amplification,
`results/results_ablation.json` for ablation,
`results/judge_scores_blind.json` for the Ember scores, and
`results/findings_ablation.md` for the written verdict. Anything not
in those files has not happened.

This is the same NeuronSteer architecture built for Nous Research's
Hermes agent (plugin merged into the Hermes catalog, November 2026),
moved onto Meta's stack: the open model is the body under test, and
Ember is the measurement instrument.
