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

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3
from panda3d.core import Vec4

from . import geometry


class Thirty(ShowBase):
    def __init__(self):
        super().__init__()
        self.accept('space', self.add_cube)

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


if __name__ == '__main__':
    Thirty().run()

