import salome

from reactor_maker import geometry

salome.salome_init_without_session()

from salome.geom import geomBuilder
from salome.smesh import smeshBuilder

from pathlib import Path
from math import cos, sin, pi

from .error.result import Result
from .vector.vector import vector3, vector2
from .geometry import ReactorGeometry
from .mesh import ReactorMesh


class ReactorMaker:
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self._OUTPUT_DIR = project_root.joinpath("outputs")

        self._geompy = geomBuilder.New()
        self._smesh = smeshBuilder.New()

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

    def create_geometry(
        self, center: vector3, radius: float, height: float, per_square: float
    ) -> Result:
        if per_square <= 0 or per_square >= 1:
            return Result(error="per_square must be between 0 and 1")

        center_pt = self._geompy.MakeVertex(center.x, center.y, center.z)
        direction = self._geompy.MakeVectorDXDYDZ(0, 0, 1)
        rotation_axis = self._geompy.MakeLine(center_pt, direction)

        disk = self._create_disk(center=vector2(0.0, 0.0), radius=radius)
        disk = self._geompy.MakeRotation(disk, rotation_axis, pi / 4)

        square_width = radius * per_square
        rectangle = self._create_rectangle(
            center=vector2(0.0, 0.0), size=vector2(square_width, square_width)
        )

        lines = [
            self._create_line(
                vector2(square_width / 2, square_width / 2), pi / 4, radius
            ),
            self._create_line(
                vector2(-square_width / 2, -square_width / 2), pi / 4, -radius
            ),
            self._create_line(
                vector2(-square_width / 2, square_width / 2), (3 / 4) * pi, radius
            ),
            self._create_line(
                vector2(square_width / 2, -square_width / 2), (3 / 4) * pi, -radius
            ),
        ]

        partition = self._geompy.MakePartition([disk], [rectangle, *lines])
        faces = self._geompy.SubShapeAllSortedCentres(
            partition, self._geompy.ShapeType["FACE"]
        )

        print(f"Number of faces : {len(faces)}")

        solid = self._geompy.MakePrismVecH(partition, direction, height)
        solid = self._geompy.MakeGlueFaces(solid, 1e-6)

        return Result(
            value=ReactorGeometry(
                geometry=solid, radius=radius, height=height, per_square=per_square
            )
        )

    def mesh(
        self,
        geometry: ReactorGeometry,
        square_divs: float,
        circle_divs: float,
        height_divs: float,
    ) -> Result:
        if geometry is None:
            return Result(error="Geometry has not yet been created")

        mesh = self._smesh.Mesh(geometry.geometry)

        mesh.Segment().NumberOfSegments(1)
        
        edge_square_size = geometry.per_square * geometry.radius

        vertex = self._geompy.MakeVertex(geometry.radius, 0, 0)
        edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertex)
        algo = mesh.Segment(edge)
        algo.NumberOfSegments(int((1 - square_divs) * edge_square_size))
        algo.Propagation()

        vertex = self._geompy.MakeVertex(0, geometry.radius, 0)
        edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertex)
        algo = mesh.Segment(edge)
        algo.NumberOfSegments(int((1 - square_divs) * edge_square_size))
        algo.Propagation()

        circle_size = geometry.radius - (geometry.radius * geometry.per_square) / 2
        on_line_pos = 1.1 * ((geometry.radius * geometry.per_square) / 2)
        vertex = self._geompy.MakeVertex(on_line_pos, on_line_pos, 0)
        edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertex)
        algo = mesh.Segment(edge)
        algo.NumberOfSegments(int((1 - circle_divs) * circle_size))
        algo.Propagation()

        vertex = self._geompy.MakeVertex(
            geometry.radius, geometry.radius, geometry.height / 2
        )
        edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertex)
        algo = mesh.Segment(edge)
        algo.NumberOfSegments(int((1 - height_divs) * geometry.height))
        algo.Propagation()

        mesh.Quadrangle()
        mesh.Hexahedron()

        if not mesh.Compute():
            return Result(error="Le maillage n'a pas pu être généré.")

        return Result(
            value=ReactorMesh(
                mesh=mesh,
                radius=geometry.radius,
                height=geometry.height,
                per_square=geometry.per_square,
            )
        )

    def mesh_export_to(self, filename: str, mesh) -> bool:
        if mesh is None:
            raise ValueError("Geometry has not yet been created")

        mesh.ExportSTL(f"{self._OUTPUT_DIR}/{filename}")

        return True
