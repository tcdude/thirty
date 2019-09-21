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
    # noinspection PyArgumentList
    def __init__(self):
        self._world = NodePath('world')
        self._origin = self._world.attach_new_node('origin')
        self._origin_p = self._origin.attach_new_node('origin_p')
        self._origin_h = self._origin_p.attach_new_node('origin_h')
        self._orientation = self._origin_h.attach_new_node('orientation')
        self._draw = self._orientation.attach_new_node('draw')
        self._origin_p.set_p(-90)
        self._origin_h.set_h(-90)

    def reset(self):
        self._origin.set_pos(0, 0, 0)
        self._origin.heads_up(Vec3(0, 1, 0), Vec3(0, 0, 1))
        self._orientation.set_pos_hpr(Vec3(0), Vec3(0))
        self._draw.set_pos_hpr(Vec3(0), Vec3(0))

    def setup(self, origin, direction):
        self.reset()
        self._origin.look_at(direction)
        self._origin.set_pos(origin)

    def set_pos_hp_d(self, x, y, z, h, p, d):
        """
        Update rig position, orientation and distance of draw from orientation.

        Arguments:
            x: x-axis offset as viewed from the base
            y: y-axis offset as viewed from the base
            z: direction-axis positive is forward, negative is back
            h: heading of the rig
            p: pitch of the rig
            d: distance/radius of draw
        """
        self._orientation.set_pos_hpr(x, -y, z, h, p, 0)
        self._draw.set_y(d)

    def set_hp_d(self, h, p, d=None):
        """
        Update rig orientation and optionally distance of draw from orientation.

        Arguments:
            h: heading of the rig
            p: pitch of the rig
            d: distance/radius of draw
        """
        self._orientation.set_hpr(h, p, 0)
        if d is not None:
            self._draw.set_y(d)

    def set_f(self, f):
        self._orientation.set_z(f)

    def set_d(self, d):
        self._draw.set_y(d)

    @property
    def orientation(self):
        return self._orientation

    @property
    def draw(self):
        return self._draw

    @property
    def pos(self):
        return self._draw.get_pos(self._world)

    @property
    def center_pos(self):
        pos = self._orientation.get_pos()
        hpr = self._orientation.get_hpr()
        z = self._draw.get_pos(self._origin).y
        self._orientation.set_pos_hpr(0, 0, z, 0, 0, 0)
        c_pos = self._orientation.get_pos(self._world)
        self._orientation.set_pos_hpr(pos, hpr)
        return c_pos

    @property
    def origin_pos(self):
        return self._origin.get_pos()
