# Silence-window cut. Mojo 1.0 CPU reference of src/ttfa/ref.py.
# Not the product. Do not call this from Python in a hot loop.
# Compile when you have `mojo`; prove it against tests/test_silence.py.

from collections import List


@fieldwise_init
struct Cut(Copyable, Movable):
    var index: Int
    var leftover_start: Int

    fn deferred(self) -> Bool:
        return self.index < 0


fn find_cut(pcm: List[Float32], radius: Int, eps: Float32) -> Cut:
    var n = len(pcm)
    if n == 0 or radius <= 0:
        return Cut(-1, 0)
    var win = radius
    if win > n:
        win = n

    var last: Int = -1
    var start = n - win
    while start >= 0:
        var peak: Float32 = 0.0
        var end = start + win
        var i = start
        var loud = False
        while i < end:
            var a = pcm[i]
            if a < 0.0:
                a = -a
            if a > peak:
                peak = a
                if peak >= eps:
                    loud = True
                    break
            i += 1
        if not loud and peak < eps:
            last = end - 1
            break
        start -= 1

    if last < 0:
        return Cut(-1, 0)
    return Cut(last, last + 1)
