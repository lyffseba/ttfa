# CPU SIMD kernel: last fixed-radius silence window (Inworld TTS-1 §5.1).
# Ownership: borrow the PCM span; no PythonObject in the hot loop.
# Names: Mojo 1.0 (Array not InlineArray, imm/mut/var, Int as Scalar).

from std.sys import simd_width_of

comptime WIDTH = simd_width_of[DType.float32]()


def leftover_start(imm cut: Int) -> Int:
    """First leftover sample, or 0 when the whole buffer is deferred."""
    if cut < 0:
        return 0
    return cut + 1


def _window_max_abs(
    imm ptr: Pointer[mut=False, Float32, _],
    imm start: Int,
    imm length: Int,
) -> Float32:
    """max(|x|) over pcm[start : start + length) via SIMD loads."""
    var acc = SIMD[DType.float32, WIDTH](0)
    var i = Int(0)
    while i + WIDTH <= length:
        var v = ptr.unsafe_offset(start + i).unsafe_load[width=WIDTH]()
        acc = max(acc, abs(v))
        i += WIDTH
    var mx = acc.reduce_max()
    while i < length:
        var sample = ptr[unsafe_offset=start + i]
        var a = abs(sample)
        if a > mx:
            mx = a
        i += 1
    return mx


def find_cut(
    imm pcm: Span[Float32, _],
    imm sample_rate: Int,
    imm window_radius_samples: Int,
    imm eps: Float32,
) -> Int:
    """Last sample to emit (inclusive), or -1 if no silence (defer).

    Search the last center t* whose window pcm[t*-r : t*+r] (inclusive)
    satisfies max(|x|) < eps. Emit through t*; leftover starts at t*+1.
    """
    _ = sample_rate
    var n = len(pcm)
    var r = window_radius_samples
    if n == 0 or r < 0:
        return -1
    var win = r + r + 1
    if win > n:
        return -1

    var last = n - 1 - r
    var first = r
    var ptr = pcm.unsafe_ptr().as_imm()
    var t = last
    while t >= first:
        if _window_max_abs(ptr, t - r, win) < eps:
            return t
        t -= 1
    return -1


def main():
    # All-zero Array: last valid center is n-1-r = 27 for n=32, r=4.
    var buf = Array[Float32, 32](fill=Float32(0))
    var cut = find_cut(Span(buf), 24000, 4, Float32(0.01))
    print(cut, leftover_start(cut))
