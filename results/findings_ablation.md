# Ablation arm: findings

Model: meta-llama/Llama-3.2-3B-Instruct, rebuilt on Modal T4.
Circuit: 229 neurons (layer histogram peaks at 27: 133, 26: 35).
Raw outputs: results/results_ablation.json (verbatim, authoritative).
Blind scores: results/judge_scores_blind.json; pool/key: blind_pool.json / blind_key.json.
Judge: Muse Ember in-session (no META_API_KEY or spark_call.py in env), seeded shuffle, labels stripped.

## Ablation (8 sea-evocative prompts, greedy, 80 tokens)

dose, circuit: sea-marker, quality(1-repeated n-gram), blind mean | control: same
  0.0: 1.000, 1.000, 9.00 | 1.000, 1.000, 8.88
  0.5: 1.000, 1.000, 9.00 | 1.000, 1.000, 8.88
  1.0: 1.000, 1.000, 8.88 | 1.000, 1.000, 8.88

Per-prompt blind scores (circuit, by dose): m0 [9,8,10,9,9,9,9,9], m0.5 same, m1 [9,7,10,9,9,9,9,9]. Control identical across all doses.

## Amplification (8 neutral prompts, from results.json + results_extended.json)

dose, circuit: marker, quality, blind mean | control: marker, quality, blind mean
  0.0: 0.125, 0.996, 0.00 | 0.000, 1.000, 0.00
  0.5: 0.125, 1.000, 0.88 | 0.125, 1.000, 0.88
  1.0: 0.125, 1.000, 0.88 | 0.125, 1.000, 0.88
  1.5: 0.250, 0.998, 0.75 | 0.125, 1.000, 0.88
  2.0: 0.125, 1.000, 1.13 | 0.125, 1.000, 0.88
  3.0: 0.125, 1.000, 1.13 | 0.125, 0.996, 1.00
  4.0: 0.125, 0.919, 0.25 | 0.125, 1.000, 0.88
  6.0: 0.000, 0.510, 0.00 | 0.125, 0.998, 0.88
  8.0: 0.000, 0.336, 0.00 | 0.125, 0.998, 1.25
 12.0: 0.000, 0.364, 0.00 | 0.125, 0.998, 1.38

## Verdict

No. Ablation does not remove the sea. At m=0 the circuit still gives full sea content
(8/8 prompts, marker 1.0, blind mean 9.0) and the control matches exactly.
Sea answers here are prompt-driven; the CNA circuit cannot veto them.
Consistent with amplification failing: this sea-vs-desert circuit has no causal
grip on sea content in either direction on Llama-3.2-3B-Instruct.
Strings do change under ablation (all 8 circuit outputs differ from baseline; 2 for control),
but sea content does not.

Caveat: ablation prompts hit marker ceiling 1.0, so the marker metric cannot
distinguish; a neutral-prompt ablation (m=0 vs 1 on EVAL_NEUTRAL) is the cleaner test.
Lakes scored 0 on the sea rubric (not sea).
