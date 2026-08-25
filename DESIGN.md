# ttfa design — 25 Aug 2026

First do it. Then do it right. Then do it better.

## Kill

Do not build: SpeechLM + codec + Mojo VAD + OpenAI stream as a clone of Inworld TTS-1 (Aug 2025) vs vLLM 0.9.1. That comparison is void. vLLM-Omni 0.18 already publishes 64 ms TTFP on Qwen3-TTS (H200, concurrency 1). MAX 26.5.0 (`max/v26.5.0`) registers no audio architecture and no `AUDIO_GENERATION` task. The `/v1/audio/speech` route is gone from that tag. Inworld weights are closed.

Do not write Mojo for RMS energy. Do not write a scheduler. Do not promise AMD/Apple audio on day one. Hosted inference on MAX needs Community License §3.3 ("Powered by Modular" + written approval).

## v0 — do it (this repo, now)

`find_cut(pcm, radius, eps)`: rightmost window of `radius` samples with `max(|x|) < eps`. Emit through that window. Defer if none. Python reference + tests. Mojo source is a twin, not a dependency.

This exists so a later graph can call one function. It is not the SKU.

## v1 — do it right

1. Pick **one** open Talker+Code2Wav stack that already has a serving path: Qwen3-TTS (the Omni number we have to beat).
2. Serve it with the incumbent (`vllm-omni`) first. Measure. That is the floor.
3. Two knobs only, in `next_chunk`: `initial_codec_chunk_frames` ∈ {2,4,8,16} and `decode_chunk_frames` (Omni uses 25 + 25 left context). No new scheduler. If we later sit on `max serve`, use `--enable-prioritize-first-decode` rather than writing a queue.
4. Stream **raw PCM**. No base64 on the first-byte path.
5. NVIDIA only until a bench exists on another SKU.
6. Mojo/MAX custom op: **zero**, unless `nsys` shows a D2H/H2D on the path to the first PCM byte (SpeechLM→codec pack or overlap-add stitch). Then that one op. Not silence-for-its-own-sake.

## v2 — do it better

Only after v1 loses to Omni on *measured* TTFA for a reason a kernel can fix. Then: one fused GPU hop, same weights, same box, same two clocks (TTFA vs time-to-2.0s-delivered), plus WER / click / onset so we cannot cheat.

CSM-1B + Mimi stays a fallback if Qwen3-TTS cannot be run. It is not the default.

## Acceptance

Same machine, same weights, vs vLLM-Omni ≥ 0.18:

- TTFA = time to first PCM byte at the client
- T2s = time until 2.0 s of audio is delivered (separate clock)
- First packet ≤ 250 ms of audio content
- Quality gates: WER, click at chunk joins, onset delay

If we cannot publish those four numbers, we have not shipped.
