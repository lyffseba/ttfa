import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ttfa.ref import find_cut


def test_empty_and_bad_radius():
    assert find_cut([], 16, 0.01).deferred
    assert find_cut([0.0] * 8, 0, 0.01).deferred


def test_all_silence_emits_all():
    c = find_cut([0.0] * 32, 8, 0.01)
    assert c.index == 31
    assert c.leftover_start == 32


def test_all_noise_defers():
    c = find_cut([0.4] * 32, 8, 0.01)
    assert c.deferred


def test_sine_is_voiced():
    pcm = [math.sin(i * 0.4) for i in range(64)]
    assert find_cut(pcm, 16, 0.05).deferred


def test_burst_then_silence_cuts_at_end():
    pcm = [0.8] * 20 + [0.0] * 20
    c = find_cut(pcm, 8, 0.01)
    assert c.index == 39
    assert c.leftover_start == 40


def test_burst_silence_burst_cuts_in_the_gap():
    pcm = [0.8] * 16 + [0.0] * 16 + [0.8] * 16
    c = find_cut(pcm, 8, 0.01)
    assert 23 <= c.index <= 31
    leftover = pcm[c.leftover_start :]
    assert leftover[0] == 0.0 or leftover[0] == 0.8


def test_radius_longer_than_buffer():
    c = find_cut([0.0, 0.0, 0.0], 16, 0.01)
    assert c.index == 2


def test_eps_zero_is_never_silence():
    # Contract is max(|x|) < eps, strict. eps=0 matches nothing.
    assert find_cut([0.0] * 8, 4, 0.0).deferred
    assert find_cut([0.0] * 8, 4, 1e-15).index == 7
    assert find_cut([1e-12] * 8, 4, 1e-15).deferred
