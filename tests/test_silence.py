"""Edge cases for the §5.1 silence / chunk-boundary reference."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ttfa.ref import cut_and_leftover, find_cut, leftover_start

SR = 24_000
R = 8
EPS = 0.01


def _window_max_abs(pcm, t, r):
    lo, hi = t - r, t + r
    mx = 0.0
    for v in pcm[lo : hi + 1]:
        a = abs(v)
        if a > mx:
            mx = a
    return mx


class TestLeftover(unittest.TestCase):
    def test_deferred_is_zero(self):
        self.assertEqual(leftover_start(-1), 0)

    def test_after_cut(self):
        self.assertEqual(leftover_start(7), 8)


class TestEmptyAndDegenerate(unittest.TestCase):
    def test_empty(self):
        cut, left = cut_and_leftover([], SR, R, EPS)
        self.assertEqual(cut, -1)
        self.assertEqual(left, 0)

    def test_radius_greater_than_len(self):
        pcm = [0.0] * 10
        cut, left = cut_and_leftover(pcm, SR, 20, EPS)
        self.assertEqual(cut, -1)
        self.assertEqual(left, 0)

    def test_radius_equals_len_cannot_fit(self):
        # window is 2r+1, so r == n never fits unless n == 1 and r == 0
        pcm = [0.0] * 8
        self.assertEqual(find_cut(pcm, SR, 8, EPS), -1)

    def test_negative_radius_defers(self):
        self.assertEqual(find_cut([0.0, 0.0], SR, -1, EPS), -1)


class TestAllZeros(unittest.TestCase):
    def test_last_center_is_n_minus_one_minus_r(self):
        n = 64
        r = 10
        pcm = [0.0] * n
        cut, left = cut_and_leftover(pcm, SR, r, EPS)
        self.assertEqual(cut, n - 1 - r)
        self.assertEqual(left, cut + 1)
        self.assertLess(_window_max_abs(pcm, cut, r), EPS)

    def test_exact_fit(self):
        r = 5
        pcm = [0.0] * (2 * r + 1)
        self.assertEqual(find_cut(pcm, SR, r, EPS), r)


class TestAllNoise(unittest.TestCase):
    def test_no_window_below_eps(self):
        pcm = [0.25 + ((i * 17) % 50) / 200.0 for i in range(128)]
        cut, left = cut_and_leftover(pcm, SR, R, EPS)
        self.assertEqual(cut, -1)
        self.assertEqual(left, 0)


class TestSine(unittest.TestCase):
    def test_full_scale_sine_defers(self):
        n = 256
        pcm = [math.sin(2.0 * math.pi * 440.0 * i / SR) for i in range(n)]
        self.assertEqual(find_cut(pcm, SR, 16, EPS), -1)

    def test_tiny_sine_is_silence(self):
        n = 64
        r = 8
        pcm = [1e-4 * math.sin(2.0 * math.pi * i / 32.0) for i in range(n)]
        cut = find_cut(pcm, SR, r, EPS)
        self.assertEqual(cut, n - 1 - r)


class TestBurstSilenceBurst(unittest.TestCase):
    def test_cuts_at_last_interior_silence(self):
        r = 10
        burst = [0.5] * 40
        silence = [0.0] * 50
        pcm = burst + silence + burst
        # Silence occupies [40, 89]. A radius-10 window fits for
        # centers t in [50, 79]. The last one is 79.
        cut, left = cut_and_leftover(pcm, SR, r, EPS)
        self.assertEqual(cut, 79)
        self.assertEqual(left, 80)
        self.assertLess(_window_max_abs(pcm, cut, r), EPS)
        # Next center would include the second burst.
        self.assertGreaterEqual(_window_max_abs(pcm, cut + 1, r), EPS)

    def test_trailing_silence_preferred_over_earlier(self):
        r = 4
        pcm = [0.8] * 20 + [0.0] * 20 + [0.8] * 10 + [0.0] * 30
        cut = find_cut(pcm, SR, r, EPS)
        # Trailing silence [50, 79]; last center = 79 - 4 = 75.
        self.assertEqual(cut, 75)


class TestEpsZero(unittest.TestCase):
    def test_only_exact_zeros_count(self):
        pcm = [1e-12] * 32
        self.assertEqual(find_cut(pcm, SR, 4, 0.0), -1)

    def test_exact_zeros_still_fail_strict_lt(self):
        # Paper: max(|x|) < eps. Zero is not < 0, so eps=0 never cuts.
        self.assertEqual(find_cut([0.0] * 32, SR, 4, 0.0), -1)

    def test_strict_less_than_eps(self):
        # A window whose peak equals eps is voiced.
        r = 2
        pcm = [0.0] * 16
        pcm[10] = EPS
        cut = find_cut(pcm, SR, r, EPS)
        # Centers whose window includes index 10 cannot qualify.
        if cut >= 0:
            self.assertTrue(cut + r < 10 or cut - r > 10)


class TestRadiusZero(unittest.TestCase):
    def test_single_sample_window(self):
        pcm = [0.4, 0.3, 0.0, 0.2]
        cut, left = cut_and_leftover(pcm, SR, 0, EPS)
        self.assertEqual(cut, 2)
        self.assertEqual(left, 3)


class TestContract(unittest.TestCase):
    def test_leftover_matches_formula(self):
        cases = [
            ([0.0] * 20, 3, EPS),
            ([0.9] * 20, 3, EPS),
            ([], 3, EPS),
            ([0.0] * 4, 10, EPS),
        ]
        for pcm, r, eps in cases:
            cut, left = cut_and_leftover(pcm, SR, r, eps)
            self.assertEqual(left, leftover_start(cut))
            self.assertEqual(left, 0 if cut < 0 else cut + 1)


if __name__ == "__main__":
    unittest.main()
