"""
Provides a representation of a mesh with convenience functions.
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

from math import cos
from math import radians

from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import GeomVertexWriter
from panda3d.core import Geom
from panda3d.core import GeomTriangles
from panda3d.core import GeomNode
from panda3d.core import Vec2
from panda3d.core import Vec3
from panda3d.core import Vec4

from . import tools


# noinspection PyArgumentList
class VertexArray(object):
    def __init__(self, name='Unnamed Shape'):
        self._name = name
        self._vert_data = GeomVertexData(
            self._name,
            GeomVertexFormat.get_v3n3c4t2(),
            Geom.UH_static
        )
        self._vert_writer = GeomVertexWriter(self._vert_data, 'vertex')
        self._norm_writer = GeomVertexWriter(self._vert_data, 'normal')
        self._color_writer = GeomVertexWriter(self._vert_data, 'color')
        self._tex_writer = GeomVertexWriter(self._vert_data, 'tex')
        self._prim = GeomTriangles(Geom.UH_static)

        self._v_id = 0

    def set_num_rows(self, num_rows):
        self._vert_data.set_num_rows(num_rows)

    def add_row(self, point, normal, color, tex):
        self._vert_writer.add_data3(point)
        self._norm_writer.add_data3(normal)
        self._color_writer.add_data4(color)
        self._tex_writer.add_data2(tex)
        self._v_id += 1
        return self._v_id - 1

    def add_triangle(self, va, vb, vc):
        self._prim.add_vertices(va, vb, vc)

    def get_node(self):
        geom = Geom(self._vert_data)
        geom.add_primitive(self._prim)
        node = GeomNode(self._name)
        node.add_geom(geom)
        return node


class Mesh(object):
    """
    Container for data related to the mesh. Provides export to Panda Node.
    """

    def __init__(self, name='unnamed shape'):
        self._name = name
        self._points = {}
        self._vertices = {}
        self._triangles = {}
        self._v_id = 0
        self._t_id = 0

    def add_vertex(self, point, color=Vec4(1), tex_coord=Vec2(0)):
        """
        Return vertex id, while avoiding duplicate vertices.

        Arguments:
            point: Vec3
            color: Vec4
            tex_coord: Vec2 texture coordinates
        """
        if point not in self._points:
            self._points[point] = self._Point(point)
        return self._points[point].add_vertex(color, tex_coord, self)

    def add_triangle(self, va, vb, vc):
        """Return triangle id."""
        self._triangles[self._t_id] = self._Triangle(va, vb, vc)
        self._t_id += 1
        return self._t_id - 1

    def export(self, flat_shading=True, flat_color=True, edge_angle=80.0):
        """
        Return a Panda3D Node of the mesh. By default uses face normals with
        averaged color per face, if `flat_shading` is ``False`` uses smooth,
        per vertex normals.

        Arguments:
            flat_shading: bool
            flat_color: bool
            edge_angle: angle in degrees at which to make sharp edges.
        """
        va = VertexArray(self._name)
        if flat_shading:
            va.set_num_rows(self._t_id * 3)
            for t in self._triangles.values():
                c = None
                if flat_color:
                    c = Vec4(0)
                    for v in t:
                        c += v.color
                    c /= 3
                t_v = [
                    va.add_row(
                        v.point,
                        t.normal,
                        c if flat_color else v.color,
                        v.tex_coord
                    ) for v in t
                ]
                va.add_triangle(*t_v)
        else:
            self._compute_smooth_normals(edge_angle)
            va.set_num_rows(self._v_id)
            v2v = {}
            for v in self._vertices.values():
                v2v[v] = va.add_row(v.point, v.normal, v.color, v.tex_coord)
            for t in self._triangles.values():
                triangle = [v2v[v] for v in t]
                va.add_triangle(*triangle)
        return va.get_node()

    def _compute_smooth_normals(self, edge_angle):
        split_cos = cos(radians(edge_angle))
        for p in self._points:
            tris = {
                t: self._vertices[v_id]
                for v_id in p.vertices
                for t in self._vertices[v_id].triangles
            }
            groups = []
            for t in tris:
                if not groups:
                    groups.append([t])
                    continue
                g_id = -1
                t_normal = t.normal
                for i, g in enumerate(groups):
                    g_id = i
                    for tt in g:
                        if t_normal.dot(tt.normal) > split_cos:
                            g_id = -1
                            break
                    if g_id == i:
                        break
                if g_id != -1:
                    groups[g_id].append(t)
                else:
                    groups.append([t])
            normals = []
            for g in groups:
                n = Vec3(0)
                for t in g:
                    n += t.normal_mag
                normals.append(n.normalized())

            for g, n in zip(groups, normals):
                for t in g:
                    tris[t].normal = n

    def insert_unique_vertex(self, point, color, tex_coord):
        """
        Return vertex id of a new vertex, not considering duplicate vertices.

        Arguments:
            point: Vec3
            color: Vec4
            tex_coord: Vec2
        """
        self._vertices[self._v_id] = self._Vertex(point, color, tex_coord)
        self._v_id += 1
        return self._v_id - 1

    class _Triangle(object):
        def __init__(self, va, vb, vc):
            self._va = va
            self._vb = vb
            self._vc = vc
            va.add_to_triangle(self)
            vb.add_to_triangle(self)
            vc.add_to_triangle(self)
            self._normal_mag = tools.tri_face_norm(va, vb, vc, False)
            self._normal = self._normal_mag.normalized()

        @property
        def normal(self):
            return self._normal

        @property
        def normal_mag(self):
            return self._normal_mag

        def __getitem__(self, item):
            if item == 0:
                return self._va
            elif item == 1:
                return self._vb
            elif item == 2:
                return self._vc
            else:
                raise IndexError

        def __setitem__(self, key, value):
            if key == 0:
                self._va = value
            elif key == 1:
                self._vb = value
            elif key == 2:
                self._vc = value
            else:
                raise IndexError

    class _Point(object):
        def __init__(self, point):
            self._point = point
            self._combinations = {}
            self._vertex_normals = []

        def add_vertex(self, color, tex_coord, mesh):
            c_id = (color, tex_coord)
            if c_id in self._combinations:
                return self._combinations[c_id]
            self._combinations[c_id] = mesh.insert_unique_vertex(
                self._point,
                color,
                tex_coord
            )
            return self._combinations[c_id]

        @property
        def vertices(self):
            return self._combinations.values()

    class _Vertex(object):
        def __init__(self, point, color, tex_coord):
            self._point = point
            self._color = color
            self._tex_coord = tex_coord
            self._triangles = []
            self._triangle_groups = []
            self._normal = Vec3(-2)

        def add_to_triangle(self, triangle):
            self._triangles.append(triangle)

        @property
        def triangles(self):
            return self._triangles

        @property
        def normal(self):
            return self._normal

        @normal.setter
        def normal(self, value):
            self._normal = value

        @property
        def point(self):
            return self._point

        @property
        def color(self):
            return self._color

        @property
        def tex_coord(self):
            return self._tex_coord
