"""
Main application
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

import random
import sys

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3
from panda3d.core import Vec4

from . import geometry


class Thirty(ShowBase):
    def __init__(self):
        super().__init__()
        self.accept('c', self.add_cube)
        self.accept('p', self.add_prism)
        self.accept('f1', self.toggle_wireframe)
        self.accept('escape', sys.exit, [0])

    def add_cube(self):
        x = random.uniform(-100, 100)
        y = random.uniform(-100, 100)
        z = random.uniform(-100, 100)
        l = random.randint(1, 80)
        w = random.randint(1, 80)
        h = random.randint(1, 80)
        self.render.attach_new_node(
            geometry.cuboid(
                Vec3(x, y, z),
                (l, w, h),
                Vec3(0, 0, 1).normalized()
            )
        )
        print(Vec3(x, y, z), (l, w, h), Vec3(x, y, z).normalized())

    def add_prism(self):
        x = random.uniform(-100, 100)
        y = random.uniform(-100, 100)
        z = random.uniform(-100, 100)
        r = random.uniform(1, 40)
        l = random.randint(1, 80)
        p = random.randint(3, 20)
        s = random.randint(1, 10)
        self.render.attach_new_node(
            geometry.prism(
                Vec3(x, y, z),
                p,
                r,
                l,
                Vec3(x, y, z).normalized(),
                segments=s
            )
        )


if __name__ == '__main__':
    Thirty().run()

