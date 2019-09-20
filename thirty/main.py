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
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from direct.interval.LerpInterval import LerpHprInterval

from . import geometry


class Thirty(ShowBase):
    def __init__(self):
        super().__init__()
        self.set_background_color(Vec4(0, 0, 0, 1))
        self.accept('b', self.add_cube)
        self.accept('c', self.add_cone)
        self.accept('p', self.add_prism)
        self.accept('d', self.add_dome)
        self.accept('t', self.add_tree)
        self.accept('f1', self.toggle_wireframe)
        self.accept('escape', sys.exit, [0])
        dl = DirectionalLight('sun')
        dl.set_color_temperature(8000)
        dl_np = self.render.attach_new_node(dl)
        al = AmbientLight('moon')
        al.set_color(Vec4(0.2, 0.2, 0.2, 1))
        al_np = self.render.attach_new_node(al)
        self.render.set_light(dl_np)
        self.render.set_light(al_np)
        self.render.set_shader_auto(True)
        LerpHprInterval(dl_np, 5, (360, 0, 0)).loop()

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
                Vec3(x, y, z).normalized()
            )
        )

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


    def add_cone(self):
        x = random.uniform(-100, 100)
        y = random.uniform(-100, 100)
        z = random.uniform(-100, 100)
        r1 = random.uniform(1, 40)
        if random.random() < 0.5:
            r2 = 0
        else:
            r2 = random.uniform(1, 40)
        l = random.randint(1, 80)
        p = random.randint(12, 40)
        s = random.randint(1, 10)
        self.render.attach_new_node(
            geometry.cone(
                Vec3(x, y, z),
                Vec3(x, y, z).normalized(),
                (r1, r2),
                p,
                l,
                segments=s
            )
        )


    def add_dome(self):
        x = random.uniform(-100, 100)
        y = random.uniform(-100, 100)
        z = random.uniform(-100, 100)
        r = random.uniform(4, 40)
        p = random.randint(10, 30)
        self.render.attach_new_node(
            geometry.dome(
                Vec3(x, y, z),
                Vec3(x, y, z).normalized(),
                p,
                r
            )
        )

    def add_tree(self):
        stem = geometry.cone(
            Vec3(0, 0, 0),
            Vec3(0, 1, 0),
            (0.5, 0.2),
            polygon=12,
            height=10,
            segments=10,
            color=Vec4(0.59, 0.27, 0, 1),
            normal_as_color=False
        )
        greens = [stem]
        for i in range(8):
            r = 2.0 - i * 0.2, 1.4 - i * 0.2
            z =  -2 + i
            greens.append(geometry.cone(
                Vec3(0, 0, z),
                Vec3(0, 1, 0),
                r,
                polygon=12,
                height=1,
                segments=1,
                color=Vec4(0.08, 0.86, 0, 1),
                normal_as_color=False
            ))
        np = self.render.attach_new_node('tree')
        for n in greens:
            np.attach_new_node(n)
        x = random.uniform(-100, 100)
        y = random.uniform(-100, 100)
        z = random.uniform(-2, 3)
        s = random.uniform(0.5, 2.5)
        np.set_pos(x, y, z)
        np.set_scale(s)


if __name__ == '__main__':
    Thirty().run()

