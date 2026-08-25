"""Reference cut: emit only at a trailing non-voicing window.

Contract (Inworld TTS-1 §5.1, implemented here as a primitive — not a product):
search the rightmost window of `radius` samples where max(|x|) < eps.
Return that window's last index (inclusive). If no such window exists, defer.

This is a host-side reference. Do not treat it as a reason to write Mojo.
A Mojo/MAX op earns its keep only if a profiler shows this cut on the
device-to-host path of the first PCM byte.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cut:
    index: int
    leftover_start: int

    @property
    def deferred(self) -> bool:
        return self.index < 0


def find_cut(pcm: list[float], radius: int, eps: float) -> Cut:
    n = len(pcm)
    if n == 0 or radius <= 0:
        return Cut(-1, 0)
    if radius > n:
        radius = n

    last = -1
    # Rightmost window first so we can stop at the first hit.
    start = n - radius
    while start >= 0:
        peak = 0.0
        end = start + radius
        i = start
        while i < end:
            a = pcm[i]
            if a < 0.0:
                a = -a
            if a > peak:
                peak = a
                if peak >= eps:
                    break
            i += 1
        if peak < eps:
            last = end - 1
            break
        start -= 1

    if last < 0:
        return Cut(-1, 0)
    return Cut(last, last + 1)
