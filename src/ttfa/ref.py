"""Python reference for the Inworld TTS-1 §5.1 silence cut.

Contract
--------
Input:  PCM float32-mono samples, sample_rate, window_radius_samples, eps.
Output: cut index = last sample to emit, inclusive; -1 if no silence (defer).
        leftover_start = cut + 1, or 0 when deferred.

A window of radius r centered at t* is pcm[t* - r : t* + r] inclusive
(length 2r + 1). The last (rightmost) such window with max(|x|) < eps
wins. Emit through the center; keep the tail for the next chunk.
Concatenate only at that non-voicing point. sample_rate is accepted so
callers can keep a time-based radius; the kernel itself is sample-index.
"""

from __future__ import annotations

from typing import Sequence


def leftover_start(cut: int) -> int:
    """First leftover sample, or 0 when the whole buffer is deferred."""
    return 0 if cut < 0 else cut + 1


def find_cut(
    pcm: Sequence[float],
    sample_rate: int,
    window_radius_samples: int,
    eps: float,
) -> int:
    """Last sample to emit (inclusive), or -1 if no silence window fits.

    Search right-to-left for the last center t* whose window
    max(|pcm[t* - r : t* + r]|) < eps. Empty buffers, negative radius,
    and radius that cannot fit (2r + 1 > n) defer.
    """
    del sample_rate  # radius is already in samples
    n = len(pcm)
    r = int(window_radius_samples)
    if n == 0 or r < 0:
        return -1
    win = r + r + 1
    if win > n:
        return -1

    last = n - 1 - r
    first = r
    t = last
    while t >= first:
        mx = 0.0
        i = t - r
        end = t + r
        while i <= end:
            v = pcm[i]
            a = v if v >= 0.0 else -v
            if a > mx:
                mx = a
            i += 1
        if mx < eps:
            return t
        t -= 1
    return -1


def cut_and_leftover(
    pcm: Sequence[float],
    sample_rate: int,
    window_radius_samples: int,
    eps: float,
) -> tuple[int, int]:
    """(cut, leftover_start) in one call."""
    cut = find_cut(pcm, sample_rate, window_radius_samples, eps)
    return cut, leftover_start(cut)
