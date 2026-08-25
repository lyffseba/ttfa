# ttfa

Time-to-first-audio. **v0 is the silence / chunk-boundary kernel only.**

Streaming TTS concatenates PCM at a *non-voicing* point (Inworld TTS-1 §5.1):
search the last fixed-radius window with `max(|x|) < eps`, emit through that
center, keep the leftover. No cut → defer the whole buffer (`cut = -1`).

## Run

```bash
git clone https://github.com/lyffseba/ttfa.git && cd ttfa
PYTHONPATH=src python -m unittest tests.test_silence -v
```

Optional Mojo 1.0 kernel (CPU SIMD, no PythonObject in the loop):

```bash
uv pip install mojo          # or: pixi add mojo
mojo src/ttfa/silence.mojo   # smoke: all-zero buffer prints cut leftover
```

If `mojo` is not installed, the `.mojo` source still lands; the Python
reference is the correctness baseline.

## v0 vs v1

| | v0 (this) | v1 (not this repo yet) |
|---|---|---|
| What | silence cut + leftover | MAX graph + CSM-1B + Mimi + `POST /v1/audio/speech` |
| Weights | none | none in-tree (caller supplies) |
| Server / codec | no | yes, later |

**Inworld bar (target, not a claim):** 200 ms first chunk; ~70% faster first 2 s
vs vLLM 0.9.1 on B200. v0 does not measure that.

Apache-2.0 (see `LICENSE`). No second license, no HF weights, no Inworld code.
