"""
Helper functions to easily create various shapes.
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

from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import GeomVertexWriter
from panda3d.core import Geom
from panda3d.core import GeomTriangles
from panda3d.core import GeomNode
from panda3d.core import Vec3
from panda3d.core import Vec4


def tangents(normal):
    x, y, z = normal
    x, y, z = abs(x), abs(y), abs(z)
    v_max = max(x, y, z)
    v_min = min(x, y, z)
    if x == v_max:
        d_max = 0
        if y == v_min:
            u = Vec3(0, 1, 0)
        else:
            u = Vec3(0, 0, 1)
    elif y == v_max:
        d_max = 1
        if x == v_min:
            u = Vec3(-1, 0, 0)
        else:
            u = Vec3(0, 0, 1)
    else:
        d_max = 2
        if x == v_min:
            u = Vec3(1, 0, 0)
        else:
            u = Vec3(0, 1, 0)

    if normal[d_max] < 0:
        u *= -1

    v_tangent = normal.cross(u)
    u_tangent = normal.cross(-v_tangent)
    return u_tangent, v_tangent


def quad(origin, bounds, normal):
    """
    Return 4-Tuple of Vec3 that make up the quad with ccw winding.

    Arguments:
        origin: center of the quad
        bounds: 2-Tuple of length and width
        normal: normal vector of the quad
    """
    u_tangent, v_tangent = tangents(normal)
    u_tangent *= bounds[0]
    v_tangent *= bounds[1]

    p1 = origin - u_tangent - v_tangent
    p2 = origin + u_tangent - v_tangent
    p3 = origin + u_tangent + v_tangent
    p4 = origin - u_tangent + v_tangent

    return p1, p2, p3, p4


def cuboid(origin, bounds, normal, color=Vec4(1)):
    """
    Return GeomNode of the cuboid,

    Arguments:
        origin: center of the cuboid
        bounds: 3-Tuple of length, width and height
        normal: normal vector of the up face
    """
    u_tangent, v_tangent = tangents(normal)
    up = quad(origin + normal * bounds[2], bounds[:2], normal)
    down = quad(origin - normal * bounds[2], bounds[:2], -normal)
    right = quad(
        origin + u_tangent * bounds[0],
        bounds[1:],
        u_tangent)
    left = quad(
        origin - u_tangent * bounds[0],
        bounds[1:],
        -u_tangent
    )
    front = quad(
        origin - v_tangent * bounds[1],
        (bounds[0], bounds[2]),
        -v_tangent
    )
    back = quad(
        origin + v_tangent * bounds[1],
        (bounds[0], bounds[2]),
        v_tangent
    )

    v_data = GeomVertexData(
        'cuboid',
        GeomVertexFormat.get_v3n3c4(),
        Geom.UHStatic
    )
    v_data.set_num_rows(24)
    vert_writer = GeomVertexWriter(v_data, 'vertex')
    norm_writer = GeomVertexWriter(v_data, 'normal')
    color_writer = GeomVertexWriter(v_data, 'color')
    verts = up + down + right + left + front + back
    norms = (normal, ) * 4 + (-normal, ) * 4
    norms += (u_tangent, ) * 4 + (-u_tangent, ) * 4
    norms += (-v_tangent, ) * 4 + (v_tangent, ) * 4
    for v, n in zip(verts, norms):
        vert_writer.add_data3(v)
        norm_writer.add_data3(n)
        color_writer.add_data4(color)
    prim = GeomTriangles(Geom.UHStatic)
    for i in range(6):
        v0 = i * 4
        v1 = v0 + 1
        v2 = v1 + 1
        v3 = v2 + 1
        prim.add_vertices(v0, v1, v2)
        prim.add_vertices(v2, v3, v0)

    geom = Geom(v_data)
    geom.add_primitive(prim)
    node = GeomNode('cuboid')
    node.add_geom(geom)
    return node


def prism(origin, polygon, length, direction, center_offset=0.5, segments=1):
    """
    Return GeomNode of prism.

    Arguments:
        origin: Mesh origin
        polygon: Number of vertices in the base polygon (3+)
        length: Length of the prism
        direction: Normalized vector
        center_offset: Optional float 0..1, indicating where the origin lies
        segments: number of segments between base and top
    """
    pass
