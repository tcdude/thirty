"""
Provides a basic drawing NodePath setup.
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

from panda3d.core import NodePath
from panda3d.core import Vec3


class Draw(object):
    def __init__(self):
        self._world = NodePath('world')
        self._origin = self._world.attach_new_node('origin')
        self._orientation = self._origin.attach_new_node('orientation')
        self._draw = self._orientation.attach_new_node('draw')

    def reset(self):
        self._origin.set_pos(0, 0, 0)
        self._origin.heads_up(Vec3(0, 1, 0), Vec3(0, 0, 1))
        self._orientation.set_pos_hpr(Vec3(0), Vec3(0))
        self._draw.set_pos_hpr(Vec3(0), Vec3(0))

    def setup(self, origin, forward, up=None):
        self.reset()
        if up is not None:
            self._origin.heads_up(forward, up)
        else:
            self._origin.look_at(forward)
        self._origin.set_pos(origin)

    @property
    def orientation(self):
        return self._orientation

    @property
    def draw(self):
        return self._draw

    @property
    def pos(self):
        return self._draw.get_pos(self._world)
