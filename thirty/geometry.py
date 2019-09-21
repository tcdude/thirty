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

from panda3d.core import Vec3
from panda3d.core import Vec4

import numpy as np

from . import draw
from . import tools
from . import mesh

NAC = True
D = draw.Draw()


def _populate_triangles(m, verts, wrap_around=True):
    for i in range(len(verts) - 1):
        upper = verts[i + 1]
        lower = verts[i]
        for u, l in tools.connect_lines(len(upper), len(lower), wrap_around):
            triangle = [upper[v] for v in u] + [lower[v] for v in l]
            m.add_triangle(*triangle)


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

    Args:
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
    D.setup(origin, direction)
    steps = np.linspace(
        -length * center_offset,
        length * (1.0 - center_offset),
        segments + 1
    )

    m = mesh.Mesh('prism')
    D.set_f(steps[0])
    D.set_d(0)
    verts = [[m.add_vertex(D.pos, color)]]
    D.set_d(radius)
    for z in steps:
        D.set_f(z)
        line = []
        for h in np.linspace(0, 360, polygon, endpoint=False):
            D.set_hp_d(h, 0)
            line.append(m.add_vertex(D.pos, color))
        verts.append(line)

    D.set_d(0)
    verts.append([m.add_vertex(D.pos, color)])

    _populate_triangles(m, verts)
    return m.export(normal_as_color=normal_as_color)


def cuboid(origin, bounds, direction, color=Vec4(1), normal_as_color=NAC):
    """
    Return GeomNode of the cuboid,

    Args:
        origin: center of the cuboid
        bounds: 3-Tuple of length, width and height
        direction: normal vector of the up face
        color: Vec4
        normal_as_color: whether to use vertex normal as color
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

    D.setup(origin, direction)
    m = mesh.Mesh('cuboid')
    for f in faces:
        pts = []
        for p in f:
            D.set_pos_hp_d(p.x, p.y, p.z, 0, 0, 0)
            pts.append(m.add_vertex(D.pos, color))
        m.add_triangle(*reversed(pts[:3]))
        m.add_triangle(pts[0], *reversed(pts[2:]))
    return m.export(normal_as_color=normal_as_color)


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

    Args:
        origin: Vec3
        direction: Vec3
        radii: 2-Tuple with base and top radius
        polygon: number of vertices of the base polygon
        height: float
        segments: number of segments from base to top
        center_offset: float 0..1 z-origin by height
        top_offset: 2-Tuple x, y offset for top
        color: Vec4
        normal_as_color: whether to use the vertex normal as color
    """
    D.setup(origin, direction)
    m = mesh.Mesh('cone')

    h_steps = np.linspace(0, 360, polygon, endpoint=False)
    r_steps = np.linspace(*radii, segments + 1)
    x_steps = np.linspace(0, top_offset[0], segments + 1)
    y_steps = np.linspace(0, top_offset[1], segments + 1)
    z_steps = np.linspace(
        -height * center_offset,
        height * (1 - center_offset),
        segments + 1
    )

    last = len(r_steps) - 1
    verts = []
    for i, (r, x, y, z) in enumerate(zip(r_steps, x_steps, y_steps, z_steps)):
        D.set_pos_hp_d(x, y, z, 0, 0, r)
        if r == 0:
            verts.append([m.add_vertex(D.pos, color)])
            continue

        if i == 0:
            D.set_d(0)
            verts.append([m.add_vertex(D.pos, color)])
            D.set_d(r)

        line = []
        for h in h_steps:
            D.set_hp_d(h, 0)
            line.append(m.add_vertex(D.pos, color))
        verts.append(line)

        if i == last:
            D.set_d(0)
            verts.append([m.add_vertex(D.pos, color)])

    _populate_triangles(m, verts)
    return m.export(False, edge_angle=80, normal_as_color=normal_as_color)


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

    Args:
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


def sphere(
        origin,
        direction,
        polygon,
        radius,
        h_deg=360,
        p_from_deg=-90,
        p_to_deg=90,
        h_offset=0,
        color=Vec4(1),
        normal_as_color=NAC
):
    """
    Return a Node of a parametric sphere.

    Args:
        origin:
        direction:
        polygon:
        radius:
        h_deg:
        p_from_deg:
        p_to_deg:
        h_offset:
        color:
        normal_as_color:

    Returns: GeomNode
    """
    if not (-90 <= p_from_deg < 90):
        raise ValueError('illegal p_from_deg')
    if not (-90 < p_to_deg <= 90) or p_to_deg <= p_from_deg:
        raise ValueError('illegal p_to_deg or not p_to_deg > p_from_deg')
    if not (0 < h_deg <= 360):
        raise ValueError('illegal h_deg')
    if polygon < 3:
        raise ValueError('polygon must be >= 3')
    if not radius or radius < 0:
        raise ValueError('radius must be a positive, non-zero float/int')

    segments = max(2, polygon // 2 + 1)  # TODO: account for partial sphere
    wrap_around = h_deg == 360
    D.setup(origin, direction)
    m = mesh.Mesh('sphere')
    p_steps = np.linspace(p_from_deg, p_to_deg, segments + 1)
    h_steps = np.linspace(0, h_deg, polygon, endpoint=False)
    last = len(p_steps) - 1
    verts = []
    h_slice = []
    slice_top = None
    slice_bottom = None
    for i, p in enumerate(p_steps):
        D.set_hp_d(h_offset, p, radius)
        if i == 0:
            if p == -90:
                verts.append([m.add_vertex(D.pos, color)])
            else:
                verts.append([m.add_vertex(D.center_pos, color)])
            if not wrap_around:
                h_slice.append(verts[-1][-1])
                slice_bottom = m[verts[-1][-1]].point
            if p == -90:
                continue

        if i < last or p < 90:
            line = []
            for j, h in enumerate(h_steps):
                D.set_hp_d(h + h_offset, p)
                line.append(m.add_vertex(D.pos, color))
                if not wrap_around:
                    if j == 0:
                        h_slice.insert(0, line[-1])
                    elif j == polygon - 1:
                        h_slice.append(line[-1])
            verts.append(line)

        if i == last:
            if p == 90:
                verts.append([m.add_vertex(D.pos, color)])
            else:
                verts.append([m.add_vertex(D.center_pos, color)])
            if not wrap_around:
                h_slice.append(verts[-1][-1])
                slice_top = m[verts[-1][-1]].point

    _populate_triangles(m, verts, wrap_around)
    if not wrap_around:
        center = (slice_top - slice_bottom) * 0.5 + slice_bottom
        tmp_verts = [
            [m.add_vertex(center, color)],
            h_slice
        ]
        _populate_triangles(m, tmp_verts)
    return m.export(
        flat_shading=False,
        edge_angle=80,
        normal_as_color=normal_as_color
    )


def dome(
        origin,
        direction,
        polygon,
        radius,
        color=Vec4(1),
        normal_as_color=NAC
):
    """
    Return a Node of a dome/half-sphere.

    Args:
        origin: Vec3
        direction: Vec3
        polygon: number of vertices
        radius: float
        color: Vec4
        normal_as_color: whether to use the vertex normal as color
    """
    return sphere(
        origin,
        direction,
        polygon,
        radius,
        p_from_deg=0,
        color=color,
        normal_as_color=normal_as_color
    )


def capsule(
        origin,
        direction,
        polygon,
        radius,
        length,
        center_offset=0.5,
        color=Vec4(1),
        normal_as_color=NAC
):
    """
    Return a Node of a capsule.

    Args:
        origin: Vec3
        direction: Vec3
        polygon: number of vertices per ring
        radius: float
        length: float units of length between the end points
        center_offset: float 0..1 origin offset
        color: Vec4
        normal_as_color: whether to use the vertex normal as color
    """
    if polygon < 3:
        raise ValueError('polygon must be >= 3')
    if radius <= 0:
        raise ValueError('radius must be a positive, non-zero float')
    if length < 2 * radius:
        raise ValueError('length must be larger than 2 * radius')
    if not (0 <= center_offset <= 1):
        raise ValueError('center_offset must be in range 0..1')

    D.setup(origin, direction)
    D.set_d(radius)
    m = mesh.Mesh('capsule')
    c_segments = max(2, polygon // 4)
    b_segments = int((length - 2 * radius) / (radius / c_segments)) + 1
    f_steps = np.linspace(
        -center_offset * length + radius,
        (1.0 - center_offset) * length - radius,
        b_segments + 1
    )
    h_steps = np.linspace(0, 360, polygon, endpoint=False)
    verts = []
    last = len(f_steps) - 1
    for i, f in enumerate(f_steps):
        D.set_f(f)
        if i == 0:
            for p in np.linspace(-90, 0, c_segments, endpoint=False):
                if p == -90:
                    D.set_hp_d(0, p)
                    verts.append([m.add_vertex(D.pos, color)])
                    continue
                line = []
                for h in h_steps:
                    D.set_hp_d(h, p)
                    line.append(m.add_vertex(D.pos, color))
                verts.append(line)

        line = []
        for h in h_steps:
            D.set_hp_d(h, 0)
            line.append(m.add_vertex(D.pos, color))
        verts.append(line)

        if i == last:
            for p in np.linspace(90, 0, c_segments, endpoint=False)[::-1]:
                if p == 90:
                    D.set_hp_d(0, p)
                    verts.append([m.add_vertex(D.pos, color)])
                    continue
                line = []
                for h in h_steps:
                    D.set_hp_d(h, p)
                    line.append(m.add_vertex(D.pos, color))
                verts.append(line)
    _populate_triangles(m, verts)
    return m.export(
        flat_shading=False,
        edge_angle=80.0,
        normal_as_color=normal_as_color
    )
