# ttfa

Time-to-first-audio.

**v0 is a cut primitive, not a speech server.** A Mojo RMS kernel is not a product. MAX 26.5.0 ships no TTS catalog. The live baseline is vLLM-Omni on Qwen3-TTS (published 64 ms first-packet on H200). We do not chase Inworld vs vLLM 0.9.1.

## Run

```bash
python3 -m pytest tests/test_silence.py -q
```

No extra deps. `src/ttfa/ref.py` is the source of truth. `src/ttfa/silence.mojo` is the same contract in Mojo 1.0 for when a profiler says the cut sits on a device-to-host of the first PCM byte. Until then, do not call Mojo from Python in a loop.

## What v1 actually is

See [DESIGN.md](DESIGN.md). Short version: one open Qwen3-TTS, two-knob chunking, raw PCM, NVIDIA, same-box bench against Omni. No custom scheduler. No Mojo until `nsys` names the hop.

Bar, not a claim: first packet ≤ 250 ms of audio, and time-to-2.0 s delivered as a *separate* clock. WER/click/onset gates so latency cannot be bought with garbage.
