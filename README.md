# ttfa

Time-to-first-audio.

**v0 is a cut primitive, not a speech server.** Mojo compiled here as a twin of the Python reference. That is not a reason to put RMS on the GPU. MAX 26.5.0 ships no TTS catalog. The live baseline is vLLM-Omni on Qwen3-TTS (published 64 ms first-packet on H200). We do not chase Inworld vs vLLM 0.9.1.

## Run

```bash
PYTHONPATH=src python -m unittest tests.test_silence -v
```

Optional, if `mojo` is installed:

```bash
uv pip install mojo
mojo src/ttfa/silence.mojo
```

`find_cut(pcm, sample_rate, radius, eps)` → last sample to emit, or `-1` to defer. Window is the paper's `t* ± r` with `max(|x|) < eps`. Emit through the center. Keep the leftover.

## What v1 actually is

See [DESIGN.md](DESIGN.md). Short version: one open Qwen3-TTS, two-knob chunking, raw PCM, NVIDIA, same-box bench against Omni. No custom scheduler. No Mojo until `nsys` names a device-to-host on the first PCM byte.

Bar, not a claim: first packet ≤ 250 ms of audio, and time-to-2.0 s delivered as a *separate* clock. WER / click / onset so latency cannot be bought with garbage.
