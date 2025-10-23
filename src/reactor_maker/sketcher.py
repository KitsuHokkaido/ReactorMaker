from math import pi, cos, sin

from .vector.vector import vector2, vector3

class Sketcher:
    def __init__(self, builder):
        self._geompy = builder

    def _create_disk(self, center: vector2, radius: float):
        vertice_center = self._geompy.MakeVertex(center.x, center.y, 0)
        normal_vector = self._geompy.MakeVectorDXDYDZ(0, 0, 1)

        circle = self._geompy.MakeDiskPntVecR(vertice_center, normal_vector, radius)

        return circle

    def _create_line(self, center: vector2, angle: float, width: float):
        center_pt = self._geompy.MakeVertex(center.x, center.y, 0)

        x = width * (0 if abs(cos(angle)) < 1e-10 else cos(angle))
        y = width * (0 if abs(sin(angle)) < 1e-10 else sin(angle))

        other_pt = self._geompy.MakeVertex(center.x + x, center.y + y, 0)

        return self._geompy.MakeLineTwoPnt(center_pt, other_pt)

    def _create_rectangle(self, center: vector2, size: vector2):
        lines = [
            self._create_line(
                vector2(center.x - size.x / 2, center.y + size.y / 2), 0, size.x
            ),
            self._create_line(
                vector2(center.x - size.x / 2, center.y - size.y / 2), 0, size.x
            ),
            self._create_line(
                vector2(center.x - size.x / 2, center.y + size.y / 2), -pi / 2, size.y
            ),
            self._create_line(
                vector2(center.x + size.x / 2, center.y + size.y / 2), -pi / 2, size.y
            ),
        ]

        wire = self._geompy.MakeWire(lines)
        plane = self._geompy.MakeFace(wire, True)

        return plane

    def _create_square_curvature(self, center: vector2, size:vector2, per_curvature:float):
        """
        Create a square with its edges curved 

        Args:
            center          (vector2):  Position of the object, origin is the center
            size            (vector2):  Size of the figure
            per_curvature   (float):    distance between the farthest point of the edge and its projection of it with curvature 

        Returns:
            SalomeObject: The figure

        """

        if per_curvature == 0:
            raise ValueError("per_curvature must be different from zero")

        adding_x = per_curvature * (size.x / 2)
        adding_y = per_curvature * (size.y / 2)

        pts_boundary = [
            self._geompy.MakeVertex(center.x - size.x/2, center.y + size.y/2, 0),
            self._geompy.MakeVertex(center.x + size.x/2, center.y + size.y/2, 0),
            self._geompy.MakeVertex(center.x - size.x/2, center.y - size.y/2, 0),
            self._geompy.MakeVertex(center.x + size.x/2, center.y - size.y/2, 0)
        ]
        
        pts_farthest = [
            self._geompy.MakeVertex(center.x + size.x/2 + adding_x, 0, 0),
            self._geompy.MakeVertex(center.x - size.x/2 - adding_x, 0, 0),
            self._geompy.MakeVertex(0, center.y + size.y/2 + adding_y, 0),
            self._geompy.MakeVertex(0, center.y - size.y/2 - adding_y, 0),
        ]

        lines = [
            self._geompy.MakeArc(pts_boundary[1], pts_farthest[0], pts_boundary[3]), 
            self._geompy.MakeArc(pts_boundary[0], pts_farthest[1], pts_boundary[2]), 
            self._geompy.MakeArc(pts_boundary[0], pts_farthest[2], pts_boundary[1]), 
            self._geompy.MakeArc(pts_boundary[2], pts_farthest[3], pts_boundary[3]), 
        ]

        wire = self._geompy.MakeWire(lines)
        plane = self._geompy.MakeFace(wire, True)

        return plane

