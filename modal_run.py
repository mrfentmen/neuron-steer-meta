"""NeuronSteer for Meta — CNA steering run on Llama 3.2 3B (Modal).

Finds the sea-vs-desert circuit with Del's Hermes NeuronSteer engine
(engine.py, unmodified), then runs the dose scan on topic-neutral prompts:
the found circuit and a size-matched random control circuit, same doses.
Returns everything as JSON; the local entrypoint saves it to results/.

Run:
  env -u ALL_PROXY -u all_proxy ~/workspace/.modal-venv/bin/modal run modal_run.py
"""

import json
import os
import random
import sys
from pathlib import Path

import modal

HERE = Path(__file__).parent

app = modal.App("neuron-steer-meta")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "transformers", "accelerate")
    .add_local_file(str(HERE / "engine.py"), "/root/engine.py")
    .add_local_file(str(HERE / "contrast.py"), "/root/contrast.py")
)

MULTIPLIERS = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
EXTENDED_MULTIPLIERS = [0.0, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]
PRIMARY_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
FALLBACK_MODEL = "NousResearch/Llama-3.2-3B-Instruct"


@app.function(
    image=image,
    gpu="T4",
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=1800,
)
def run_experiment(multipliers: list | None = None) -> dict:
    if multipliers is None:
        multipliers = MULTIPLIERS
    sys.path.insert(0, "/root")
    # The Modal secret may expose the HF token under any of these names.
    for key in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN",
                "HUGGING_FACE_TOKEN", "HF_API_TOKEN"):
        if os.environ.get(key):
            os.environ["HF_TOKEN"] = os.environ[key]
            break
    print("env keys present:", sorted(k for k in os.environ if "HF" in k or "HUGGING" in k))

    import engine
    from contrast import EVAL_NEUTRAL, NEGATIVE_DESERT, POSITIVE_SEA, SEA_MARKER

    model = None
    tok = None
    used_model = None
    errors = {}
    for candidate in (PRIMARY_MODEL, FALLBACK_MODEL):
        try:
            model, tok = engine.load_model(candidate, allow_download=True)
            used_model = candidate
            break
        except Exception as exc:  # record and try the mirror
            errors[candidate] = f"{type(exc).__name__}: {exc}"[:500]
            engine._MODEL_CACHE.pop(candidate, None)
    if model is None:
        return {"ok": False, "errors": errors}

    print("loaded:", used_model)
    circuit = engine.find_circuit(
        model, tok, POSITIVE_SEA, NEGATIVE_DESERT, model_id=used_model,
    )
    print("circuit size:", len(circuit.neurons))

    # Size-matched random control circuit (seeded, reproducible).
    mlps = engine.mlp_modules(model)
    n_layers = len(mlps)
    inter = mlps[0].down_proj.in_features
    rng = random.Random(12345)
    seen = set()
    control_neurons = []
    while len(control_neurons) < len(circuit.neurons):
        pair = (rng.randrange(n_layers), rng.randrange(inter))
        if pair in seen:
            continue
        seen.add(pair)
        control_neurons.append(
            engine.NeuronRef(layer=pair[0], neuron=pair[1], delta=0.0))
    control = engine.Circuit(
        model_id=used_model, neurons=control_neurons,
        positive_count=len(POSITIVE_SEA), negative_count=len(NEGATIVE_DESERT))

    scan_kwargs = dict(
        prompts=EVAL_NEUTRAL, multipliers=multipliers,
        max_new_tokens=80, marker=SEA_MARKER)
    rows = engine.scan(model, tok, circuit, **scan_kwargs)
    control_rows = engine.scan(model, tok, control, **scan_kwargs)

    return {
        "ok": True,
        "model": used_model,
        "model_errors": errors,
        "circuit": circuit.to_dict(),
        "circuit_layer_histogram": circuit.layer_histogram(),
        "multipliers": multipliers,
        "scan": rows,
        "control_scan": control_rows,
        "eval_prompts": EVAL_NEUTRAL,
    }


@app.local_entrypoint()
def main(tag: str = ""):
    if tag == "extended":
        result = run_experiment.remote(EXTENDED_MULTIPLIERS)
        out = HERE / "results" / "results_extended.json"
    else:
        result = run_experiment.remote()
        out = HERE / "results" / "results.json"
    out.write_text(json.dumps(result, indent=2))
    print("saved:", out)
    if not result.get("ok"):
        print("FAILED:", json.dumps(result.get("errors"), indent=2))
        return
    print("model:", result["model"])
    print("circuit neurons:", len(result["circuit"]["neurons"]))
    for label, rows in (("circuit", result["scan"]),
                        ("control", result["control_scan"])):
        for row in rows:
            print(f"{label} m={row['multiplier']}: "
                  f"marker_rate={row['marker_rate']} "
                  f"quality={row['mean_quality']:.3f}")
