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
from panda3d.core import NodePath
from panda3d.core import Vec3
from panda3d.core import Vec4

import numpy as np


def connect_lines(upper, lower, wrap_around=True):
    """
    Return triangle indices to connect two lines of vertices.

    Arguments:
        upper: Number of vertices in the upper "line"
        lower: Number of vertices in the lower "line"
        wrap_around: (Optional) whether to connect the ends
    """
    if not (1 < upper == lower or [upper, lower].count(1) == 1):
        raise ValueError('Wrong input. upper and lower either need to be '
                         'the same and > 1 or any combination of 1 and >=2')

    if 1 in (upper, lower):
        if upper == 1:
            if wrap_around:
                return [((0, ), (i, (i + 1) % lower)) for i in range(lower)]
            else:
                return [((0, ), (i, i + 1)) for i in range(lower - 1)]
        else:
            if wrap_around:
                return [(((i + 1) % upper, i), (0, )) for i in range(upper)]
            else:
                return [((i + 1, i), (0, )) for i in range(upper - 1)]

    indices = []
    for i in range(upper if wrap_around else upper - 1):
        next_i = (i + 1) % upper
        indices.append(((i, ), (i, next_i)))
        indices.append(((next_i, i), (next_i, )))
    return indices


def tri_face_norm(p1, p2, p3):
    u = p2 - p1
    v = p3 - p1
    return Vec3(
        u.y * v.z - u.z * v.y,
        u.z * v.x - u.x * v.z,
        u.x * v.y - u.y * v.x
    ).normalized()


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


def prism(
        origin,
        polygon,
        radius,
        length,
        direction=Vec3(0, 0, 1),
        center_offset=0.5,
        segments=1,
        color=Vec4(1)
    ):
    """
    Return GeomNode of prism.

    Arguments:
        origin: Mesh origin
        polygon: Number of vertices in the base polygon (3+)
        radius: radius of the base polygon
        length: Length of the prism
        direction: Normalized vector
        center_offset: Optional float 0..1, indicating where the origin lies
        segments: number of segments between base and top
        color: Vec4
    """
    world_np = NodePath('world')
    direction_np = world_np.attach_new_node('direction')
    orientation_np = direction_np.attach_new_node('orientation')
    draw_np = orientation_np.attach_new_node('draw')
    draw_np.set_pos(radius, 0, 0)
    direction_np.look_at(*tuple(direction))
    steps = np.linspace(
        -length * center_offset,
        length * (1.0 - center_offset),
        segments + 1
    )
    verts = []
    for z in steps:
        orientation_np.set_z(z)
        line = []
        for h in np.linspace(0, 360, polygon, endpoint=False):
            orientation_np.set_h(h)
            line.append(draw_np.get_pos(world_np) + origin)
        verts.append(line)

    orientation_np.set_z(steps[0])
    base_point = orientation_np.get_pos(world_np) + origin
    orientation_np.set_z(steps[-1])
    top_point = orientation_np.get_pos(world_np) + origin
    base_triangles = connect_lines(polygon, 1)
    segment_triangles = connect_lines(polygon, polygon)
    top_triangles = connect_lines(1, polygon)

    vert_data = GeomVertexData(
        'prism',
        GeomVertexFormat.get_v3n3c4(),
        Geom.UH_static
    )

    vert_data.set_num_rows(
        len(base_triangles) * 6 + len(segment_triangles) * segments * 3
    )
    vert_writer = GeomVertexWriter(vert_data, 'vertex')
    norm_writer = GeomVertexWriter(vert_data, 'normal')
    color_writer = GeomVertexWriter(vert_data, 'color')

    base_normal = -direction
    normal_sides = []
    for i in range(polygon):
        u, l = segment_triangles[i * 2]
        pts = [verts[1][v] for v in u] + [verts[0][v] for v in l]
        normal_sides.append(tri_face_norm(*pts))

    prim = GeomTriangles(Geom.UH_static)

    # Fill vert_data and create primitives on the fly
    current_id = 0
    for u, l in base_triangles:
        triangle = [verts[0][i] for i in u] + [base_point, ]
        for v in triangle:
            vert_writer.add_data3(v)
            norm_writer.add_data3(base_normal)
            # color_writer.add_data4(color)
            color_writer.add_data4(*tuple(base_normal), 1)
        prim.add_vertices(current_id, current_id + 1, current_id + 2)
        current_id += 3

    for u, l in top_triangles:
        triangle = [top_point, ] + [verts[-1][i] for i in l]
        for v in triangle:
            vert_writer.add_data3(v)
            norm_writer.add_data3(direction)
            # color_writer.add_data4(color)
            color_writer.add_data4(*tuple(direction), 1)
        prim.add_vertices(current_id, current_id + 1, current_id + 2)
        current_id += 3

    for line_id in range(len(verts) - 1):
        upper = verts[line_id + 1]
        lower = verts[line_id]
        for i in range(polygon):
            normal = normal_sides[i]
            idx = i * 2
            for u, l in segment_triangles[idx:idx + 2]:
                triangle = [upper[v] for v in u]
                triangle += [lower[v] for v in l]
                for v in triangle:
                    vert_writer.add_data3(v)
                    norm_writer.add_data3(normal)
                    # color_writer.add_data4(color)
                    color_writer.add_data4(*tuple(normal), 1)
                prim.add_vertices(current_id, current_id + 1, current_id + 2)
                current_id += 3

    geom = Geom(vert_data)
    geom.add_primitive(prim)
    node = GeomNode('prism')
    node.add_geom(geom)
    return node
