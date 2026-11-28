# Prompt and token trace — Muse Ember usage

Project: NeuronSteer for Meta (Muse Ember Hackathon, Cerebral
Valley × Meta). This file records exactly how Muse Ember was used,
what it was given, what it returned, and what was spent.

## The judging run

- **Judge:** Muse Ember (Meta), scoring in session on
  November 27, 2026.
- **Protocol:** blind. Every generated output from both experiment
  arms was stripped of its dose and circuit labels, shuffled with
  a seeded shuffle, and presented for scoring with no condition
  information. The key linking pool IDs to conditions was held in
  a separate file and rejoined only after all scores were in.
- **What Ember received:** 208 outputs (the pool,
  `results/blind_pool.json`), 71,349 characters in total (about
  14,300 words, roughly 17,000 to 18,000 tokens at the usual
  four characters per token; that conversion is an estimate, the
  character count is measured), plus the scoring instruction:
  rate the sea content of each output from 0 to 10.
- **What Ember returned:** 208 integer scores
  (`results/judge_scores_blind.json`), summarised there by arm
  and dose. Headline values: ablation, circuit at dose 0, mean
  9.0 (scores 9, 8, 10, 9, 9, 9, 9, 9); ablation control mean
  8.88. The amplification summary is in the same file and the
  full table is written out in `results/findings_ablation.md`.
- **Pool composition:** the 208 outputs cover the amplification
  arm (8 neutral prompts × doses 0 to 12 × circuit and control,
  from `results/results.json` and `results/results_extended.json`)
  and the ablation arm (8 sea-evocative prompts × doses 0, 0.5, 1
  × circuit and control, from `results/results_ablation.json`).

## Spend

- **Meta Model API spend against the $10 hackathon credit: $0.**
  The judging above ran in a Muse Ember session, not through the
  Meta Model API: no API key was present in the run environment
  (the build sandbox's egress to api.meta.ai was blocked, which is
  recorded in the project notes), so no API calls were made and no
  credit was consumed. Nothing in this trace is an API usage
  record, and none is claimed.
- **Reproduction through the API:** `judge.py` and
  `judge_standalone.py` implement the identical blind protocol
  against the Meta Model API (model `muse-ember-1.0`). Run with a
  key, they write per-dose scores to `results/judge_scores.json`
  and record a failure, never a substitute scorer, if the API
  cannot be reached. Judging the 208-output pool through the API
  costs on the order of the pool's token volume above, well inside
  the $10 cap.

## The non-Ember runs (for completeness)

- Steering experiments ran on Modal (one T4) against
  meta-llama/Llama-3.2-3B-Instruct: circuit finding by contrastive
  attribution (229 neurons), the dose scans, and the ablation arm.
  Raw outputs: `results/results.json`,
  `results/results_extended.json`, `results/results_ablation.json`.
- Ember's role was measurement only: it generated none of the
  steered text and saw none of the condition labels while scoring.
