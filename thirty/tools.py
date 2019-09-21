"""
Various helper functions
"""

__copyright__ = """
MIT License

Copyright (c) 2019 tcdude

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from panda3d.core import Vec3


def tri_face_norm(p1, p2, p3, normalized=True):
    u = p2 - p1
    v = p3 - p1
    n = Vec3(
        u.y * v.z - u.z * v.y,
        u.z * v.x - u.x * v.z,
        u.x * v.y - u.y * v.x
    )
    return n.normalized() if normalized else n


def _connect_lines(upper, lower, wrap_around, ccw):
    """
    Internal execution of connect_lines(...).

    Args:
        upper: Number of vertices in the upper "line"
        lower: Number of vertices in the lower "line"
        wrap_around: (Optional) whether to connect the ends
        ccw: whether lines are in counter clock wise order
    """
    if not (1 < upper == lower or [upper, lower].count(1) == 1):
        raise ValueError('Wrong input. upper and lower either need to be '
                         'the same and > 1 or any combination of 1 and >=2')

    if 1 in (upper, lower):
        if upper == 1:
            if wrap_around:
                if ccw:
                    return [((0, ), (i, (i + 1) % lower)) for i in range(lower)]
                return [((0,), ((i + 1) % lower, i)) for i in range(lower)]
            else:
                if ccw:
                    return [((0, ), (i, i + 1)) for i in range(lower - 1)]
                return [((0, ), (i + 1, i)) for i in range(lower - 1)]
        else:
            if wrap_around:
                if ccw:
                    return [(((i + 1) % upper, i), (0, )) for i in range(upper)]
                return [((i, (i + 1) % upper), (0, )) for i in range(upper)]
            else:
                if ccw:
                    return [((i + 1, i), (0, )) for i in range(upper - 1)]
                return [((i, i + 1), (0, )) for i in range(upper - 1)]

    indices = []
    for i in range(upper if wrap_around else upper - 1):
        next_i = (i + 1) % upper
        if ccw:
            indices.append(((i, ), (i, next_i)))
            indices.append(((next_i, i), (next_i, )))
        else:
            indices.append(((i,), (next_i, i)))
            indices.append(((i, next_i), (next_i,)))
    return indices


_connect_lines_cache = {}


def connect_lines(upper, lower, wrap_around=True, ccw=True):
    """
    Return triangle indices to connect two lines of vertices.

    Args:
        upper: Number of vertices in the upper "line"
        lower: Number of vertices in the lower "line"
        wrap_around: (Optional) whether to connect the ends
        ccw: whether lines are in counter clock wise order
    """
    k = (upper, lower, wrap_around, ccw)
    if k not in _connect_lines_cache:
        _connect_lines_cache[k] = _connect_lines(*k)
    return _connect_lines_cache[k]
