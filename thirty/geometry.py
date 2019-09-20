"""
Helper functions to easily create various shapes.
"""
from thirty.tools import connect_lines

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

from . import draw
from . import tools


NAC = True


def vert_array(num_rows, name):
    vert_data = GeomVertexData(
        name,
        GeomVertexFormat.get_v3n3c4(),
        Geom.UH_static
    )

    vert_data.set_num_rows(num_rows)
    vert_writer = GeomVertexWriter(vert_data, 'vertex')
    norm_writer = GeomVertexWriter(vert_data, 'normal')
    color_writer = GeomVertexWriter(vert_data, 'color')
    return vert_data, vert_writer, norm_writer, color_writer


def prism(
        origin,
        polygon,
        radius,
        length,
        direction=Vec3(0, 0, 1),
        center_offset=0.5,
        segments=1,
        color=Vec4(1),
        normal_as_color=NAC
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
        normal_as_color: whether to use the normal as color
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

    vert_data, vert_writer, norm_writer, color_writer = vert_array(
        len(base_triangles) * 6 + len(segment_triangles) * segments * 3,
        'prism'
    )

    base_normal = -direction
    normal_sides = []
    for i in range(polygon):
        u, l = segment_triangles[i * 2]
        pts = [verts[1][v] for v in u] + [verts[0][v] for v in l]
        normal_sides.append(tools.tri_face_norm(*pts))

    prim = GeomTriangles(Geom.UH_static)

    # Fill vert_data and create primitives on the fly
    current_id = 0
    for u, l in base_triangles:
        triangle = [verts[0][i] for i in u] + [base_point, ]
        for v in triangle:
            vert_writer.add_data3(v)
            norm_writer.add_data3(base_normal)
            if normal_as_color:
                color_writer.add_data4(*tuple(base_normal), 1)
            else:
                color_writer.add_data4(color)
        prim.add_vertices(current_id, current_id + 1, current_id + 2)
        current_id += 3

    for u, l in top_triangles:
        triangle = [top_point, ] + [verts[-1][i] for i in l]
        for v in triangle:
            vert_writer.add_data3(v)
            norm_writer.add_data3(direction)
            if normal_as_color:
                color_writer.add_data4(*tuple(direction), 1)
            else:
                color_writer.add_data4(color)
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
                    if normal_as_color:
                        color_writer.add_data4(*tuple(normal), 1)
                    else:
                        color_writer.add_data4(color)
                prim.add_vertices(current_id, current_id + 1, current_id + 2)
                current_id += 3

    geom = Geom(vert_data)
    geom.add_primitive(prim)
    node = GeomNode('prism')
    node.add_geom(geom)
    return node


def cuboid(origin, bounds, normal, color=Vec4(1), normal_as_color=NAC):
    """
    Return GeomNode of the cuboid,

    Arguments:
        origin: center of the cuboid
        bounds: 3-Tuple of length, width and height
        normal: normal vector of the up face
    """
    dfl = Vec3(-bounds[0], -bounds[1], -bounds[2])
    dfr = Vec3(bounds[0], -bounds[1], -bounds[2])
    dbr = Vec3(bounds[0], bounds[1], -bounds[2])
    dbl = Vec3(-bounds[0], bounds[1], -bounds[2])
    ufl = Vec3(-bounds[0], -bounds[1], bounds[2])
    ufr = Vec3(bounds[0], -bounds[1], bounds[2])
    ubr = Vec3(bounds[0], bounds[1], bounds[2])
    ubl = Vec3(-bounds[0], bounds[1], bounds[2])

    faces = [
        (ufl, ufr, ubr, ubl),   # Up
        (dfl, dbl, dbr, dfr),   # Down
        (dfr, dbr, ubr, ufr),   # Right
        (dfl, ufl, ubl, dbl),   # Left
        (dfl, dfr, ufr, ufl),   # Front
        (dbl, ubl, ubr, dbr),   # Back
    ]

    world_np = NodePath('world')
    direction_np = world_np.attach_new_node('direction')
    draw_np = direction_np.attach_new_node('draw')
    direction_np.look_at(normal)
    direction_np.set_pos(origin)

    vert_data, vert_writer, norm_writer, color_writer = vert_array(
        24,
        'cuboid'
    )
    prim = GeomTriangles(Geom.UH_static)

    current_id = 0
    for f in faces:
        pts = []
        for p in f:
            draw_np.set_pos(p)
            vert = draw_np.get_pos(world_np)
            vert_writer.add_data3(vert)
            pts.append(vert)
        normal = tools.tri_face_norm(*pts[:3])

        for i in range(4):
            norm_writer.add_data3(normal)
            if normal_as_color:
                color_writer.add_data4(*tuple(normal), 1)
            else:
                color_writer.add_data4(color)
        prim.add_vertices(current_id, current_id + 1, current_id + 2)
        prim.add_vertices(current_id + 2, current_id + 3, current_id)
        current_id += 4

    geom = Geom(vert_data)
    geom.add_primitive(prim)
    node = GeomNode('cuboid')
    node.add_geom(geom)
    return node


def cone(
        origin,
        direction,
        radii,
        polygon,
        height,
        segments=1,
        center_offset=0.5,
        top_offset=(0, 0),
        color=Vec4(1),
        normal_as_color=NAC
    ):
    """
    Return a Node of a cone.

    Arguments:
        origin: Vec3
        direction: Vec3
        radii: 2-Tuple with base and top radius
        polygon: number of vertices of the base polygon
        height: float
        segments: number of segments from base to top
        center_offset: float 0..1 z-origin by height
        top_offset: 2-Tuple x, y offset for top TODO: Implement this
        color: Vec4
        normal_as_color: whether to use the vertex normal as color
    """
    vert_data, vert_writer, norm_writer, color_writer = vert_array(
        2 + polygon * (segments + 1 if 0 in radii else 2),
        'cone'
    )
    current_id = [0]

    def add_row(v, n):
        vert_writer.add_data3(v)
        norm_writer.add_data3(n)
        if normal_as_color:
            color_writer.add_data4(*tuple(n), 1)
        else:
            color_writer.add_data4(color)
        current_id[0] += 1
        return current_id[0] - 1

    world_np = NodePath('world')
    direction_np = world_np.attach_new_node('direction')
    orientation_np = direction_np.attach_new_node('orientation')
    draw_np = orientation_np.attach_new_node('draw')
    direction_np.look_at(direction)
    direction_np.set_pos(origin)

    draw_np.set_x(1)
    h_steps = np.linspace(0, 360, polygon, endpoint=False)
    normals = []
    for h in h_steps:
        orientation_np.set_h(h)
        n = draw_np.get_pos(world_np) - orientation_np.get_pos(world_np)
        n.normalize()
        normals.append(n)

    draw_np.set_pos(0, 0, -1)
    base_normal = draw_np.get_pos(world_np) - orientation_np.get_pos(world_np)
    base_normal.normalize()
    top_normal = -base_normal

    r_steps = np.linspace(*radii, segments + 1)

    draw_np.set_pos(0, 0, 0)
    z_steps = np.linspace(
        -height * center_offset,
        height * (1 - center_offset),
        segments + 1
    )

    last = len(r_steps) - 1
    verts = []
    for i, (r, z) in enumerate(zip(r_steps, z_steps)):
        orientation_np.set_z(z)
        draw_np.set_x(r)
        if r == 0:
            v_id = add_row(
                draw_np.get_pos(world_np),
                top_normal if i else base_normal
            )

            verts.append([v_id])
            continue

        if i == 0:
            line = []
            draw_np.set_x(0)
            v_id = add_row(draw_np.get_pos(world_np), base_normal)
            verts.append([v_id])
            draw_np.set_x(r)
            for h, n in zip(h_steps, normals):
                orientation_np.set_h(h)
                v_id = add_row(draw_np.get_pos(world_np), base_normal)
                line.append(v_id)
            verts.append(line)

        line = []
        for h, n in zip(h_steps, normals):
            orientation_np.set_h(h)
            v_id = add_row(draw_np.get_pos(world_np), n)
            line.append(v_id)
        verts.append(line)

        if i == last:
            line = []
            for h, n in zip(h_steps, normals):
                orientation_np.set_h(h)
                v_id = add_row(draw_np.get_pos(world_np), top_normal)
                line.append(v_id)
            verts.append(line)
            draw_np.set_x(0)
            v_id = add_row(draw_np.get_pos(world_np), top_normal)
            verts.append([v_id])

    prim = GeomTriangles(Geom.UH_static)
    for i in range(len(verts) - 1):
        upper = verts[i + 1]
        lower = verts[i]
        tri_indices = connect_lines(len(upper), len(lower))
        for u, l in tri_indices:
            triangle = [upper[v] for v in u] + [lower[v] for v in l]
            prim.add_vertices(*triangle)

    geom = Geom(vert_data)
    geom.add_primitive(prim)
    node = GeomNode('cone')
    node.add_geom(geom)
    return node


def cylinder(
        origin,
        direction,
        polygon,
        radius,
        height,
        segments=1,
        center_offset=0.5,
        color=Vec4(1),
        normal_as_color=NAC
    ):
    """
    Return a Node of a cylinder.

    Arguments:
        origin: Vec3
        direction: Vec3
        polygon: number of vertices
        radius: float
        height: float
        segments: int
        center_offset: float, origin offset from base
        color: Vec4
        normal_as_color: whether to use the vertex normal as color
    """
    return cone(
        origin,
        direction,
        polygon,
        (radius, radius),
        height,
        segments,
        center_offset,
        color=color,
        normal_as_color=normal_as_color
    )


def dome(
        origin,
        direction,
        polygon,
        radius,
        segments=None,
        color=Vec4(1),
        normal_as_color=NAC
    ):
    """
    Return a Node of a dome/half-sphere.

    Arguments:
        origin: Vec3
        direction: Vec3
        polygon: number of vertices
        radius: float
        segments: int
        color: Vec4
        normal_as_color: whether to use the vertex normal as color
    """
    segments = segments or max(2, polygon // 4 + 1)
    vert_data, vert_writer, norm_writer, color_writer = vert_array(
        2 + polygon * (segments + 1),
        'dome'
    )
    current_id = [0]

    def add_row(v, n):
        vert_writer.add_data3(v)
        norm_writer.add_data3(n)
        if normal_as_color:
            color_writer.add_data4(*tuple(n.normalized()), 1)
        else:
            color_writer.add_data4(color)
        current_id[0] += 1
        return current_id[0] - 1

    world_np = NodePath('world')
    direction_np = world_np.attach_new_node('direction')
    orientation_np = direction_np.attach_new_node('orientation')
    draw_np = orientation_np.attach_new_node('draw')
    direction_np.look_at(direction)
    direction_np.set_pos(origin)
    draw_np.set_y(radius)
    orientation_np.set_z(radius)
    verts = [[add_row(orientation_np.get_pos(world_np), direction)]]
    orientation_np.set_z(0)
    base_point = add_row(orientation_np.get_pos(world_np), -direction)
    base_normal = -direction

    h_steps = np.linspace(0, 360, polygon, endpoint=False)
    p_steps = np.linspace(0, 90, segments + 1, endpoint=False)
    p_steps = p_steps[::-1]
    last_line = []
    for i, p in enumerate(p_steps):
        line = []
        orientation_np.set_p(p)
        for h in h_steps:
            orientation_np.set_h(h)
            v = draw_np.get_pos(world_np)
            n = v - base_point
            n.normalize()
            line.append(add_row(v, n))
            if i == segments:
                last_line.append(add_row(v, (base_normal * 3 + n).normalized()))
        verts.append(line)

    prim = GeomTriangles(Geom.UH_static)
    for i in range(len(verts) - 1):
        upper = verts[i]
        lower = verts[i + 1]
        for u, l in connect_lines(len(upper), len(lower)):
            triangle = [upper[v] for v in u] + [lower[v] for v in l]
            prim.add_vertices(*triangle)

    for u, l in connect_lines(len(last_line), 1):
        triangle = [last_line[v] for v in u] + [base_point]
        prim.add_vertices(*triangle)

    geom = Geom(vert_data)
    geom.add_primitive(prim)
    node = GeomNode('dome')
    node.add_geom(geom)
    return node


def mushroom_cap(
        origin,
        direction,
        polygon,
        inner_radii,
        outer_radii,
        inner_height,
        outer_height,
        inner_color=Vec4(1),
        outer_color=Vec4(1),
        normal_as_color=NAC
    ):
    """
    Return a Node of a mushroom cap shape.

    Arguments:
        origin: Vec3
        direction: Vec3
        polygon: Number of vertices for the polygons used
        inner_radii: inner radii from inner top most to base of the cap
        outer_radii: outer radii from outer base to the top most
        inner_height: distance between base and inner top
        outer_height: distance between base and outer top
        inner_color: Vec4 color inside the cap
        outer_color: Vec4 color outside the cap
        normal_as_color: whether to use the normal vector as color
    """
    d = draw.Draw()
    d.setup(origin, direction)

