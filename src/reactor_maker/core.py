import salome

salome.salome_init_without_session()

import GEOM, SMESH
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder

from pathlib import Path
from math import pi, ceil

from .error.result import Result
from .vector.vector import vector3, vector2
from .geometry import ReactorGeometry
from .mesh import ReactorMesh
from .sketcher import Sketcher


class ReactorMaker:
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self._OUTPUT_DIR = project_root.joinpath("outputs")

        self._geompy = geomBuilder.New()
        self._smesh = smeshBuilder.New()

    def _create_group(
        self, geometry, center: vector3, reactor_dim: vector2, chimney_dim: vector2
    ) -> Result:
        radius = reactor_dim.x
        height = reactor_dim.y

        inlet = self._geompy.CreateGroup(geometry, self._geompy.ShapeType["FACE"])
        base = self._geompy.MakeVertex(center.x, center.y, center.z)
        direction = self._geompy.MakeVectorDXDYDZ(0, 0, 1)
        items = self._geompy.GetShapesOnPlaneWithLocationIDs(
            geometry, self._geompy.ShapeType["FACE"], direction, base, GEOM.ST_ON
        )
        self._geompy.UnionIDs(inlet, items)

        outlet = self._geompy.CreateGroup(geometry, self._geompy.ShapeType["FACE"])
        base = self._geompy.MakeVertex(center.x, center.y, center.z + height)
        direction = self._geompy.MakeVectorDXDYDZ(0, 0, 1)
        items = self._geompy.GetShapesOnPlaneWithLocationIDs(
            geometry, self._geompy.ShapeType["FACE"], direction, base, GEOM.ST_ON
        )
        self._geompy.UnionIDs(outlet, items)

        wall = self._geompy.CreateGroup(geometry, self._geompy.ShapeType["FACE"])
        pts = [
            self._geompy.MakeVertex(center.x + radius, center.y, center.z + height / 2),
            self._geompy.MakeVertex(center.x - radius, center.y, center.z + height / 2),
            self._geompy.MakeVertex(center.x, center.y + radius, center.z + height / 2),
            self._geompy.MakeVertex(center.x, center.y - radius, center.z + height / 2),
        ]
        faces = [self._geompy.GetFaceNearPoint(geometry, pt) for pt in pts]
        self._geompy.UnionList(wall, faces)
        return Result(value=(inlet, outlet, wall))

    def _create_base(self, sketcher, center, reactor_dim, chimney_dim, square_width):
        center_pt = self._geompy.MakeVertex(center.x, center.y, center.z)
        direction = self._geompy.MakeVectorDXDYDZ(0, 0, 1)
        rotation_axis = self._geompy.MakeLine(center_pt, direction)

        disk = sketcher._create_disk(
            center=vector2(center.x, center.y), radius=reactor_dim.x
        )
        disk = self._geompy.MakeRotation(disk, rotation_axis, pi / 4)

        rectangle = sketcher._create_square_curvature(
            center=vector2(center.x, center.y),
            size=vector2(square_width, square_width),
            per_curvature=0.1,
        )

        lines = [
            sketcher._create_line(
                vector2(square_width / 2, square_width / 2), pi / 4, reactor_dim.x
            ),
            sketcher._create_line(
                vector2(-square_width / 2, -square_width / 2), pi / 4, -reactor_dim.x
            ),
            sketcher._create_line(
                vector2(-square_width / 2, square_width / 2),
                (3 / 4) * pi,
                reactor_dim.x,
            ),
            sketcher._create_line(
                vector2(square_width / 2, -square_width / 2),
                (3 / 4) * pi,
                -reactor_dim.x,
            ),
        ]

        base_lines = [
            sketcher._create_line(
                vector2(chimney_dim.x / 2, 1.1 * (square_width / 2)),
                pi / 2,
                -1.2 * square_width,
            ),
            sketcher._create_line(
                vector2(-chimney_dim.x / 2, 1.1 * (square_width / 2)),
                pi / 2,
                -1.2 * square_width,
            ),
            sketcher._create_line(
                vector2(-1.1 * (square_width / 2), chimney_dim.x / 2),
                0,
                1.2 * square_width,
            ),
            sketcher._create_line(
                vector2(-1.1 * (square_width / 2), -chimney_dim.x / 2),
                0,
                1.2 * square_width,
            ),
        ]

        meshing_square = self._geompy.MakePartition([rectangle], [*base_lines])

        return self._geompy.MakePartition([disk], [meshing_square, *lines])

    def create_geometry(
        self,
        center: vector3,
        reactor_dim: vector2,
        chimney_dim: vector2,
        per_square: float,
        mesh_size: float,
    ) -> Result:
        nb_seg = ceil(chimney_dim.x / mesh_size)
        msh_sz = chimney_dim.x / nb_seg

        print(
            f"New characteristics mesh size to maximize the aspect ratio : {mesh_size:0.2f} ⭢ {msh_sz:0.2f}"
        )

        sketcher = Sketcher(self._geompy)

        if per_square <= 0 or per_square >= 1:
            return Result(error="per_square must be between 0 and 1")

        square_width = reactor_dim.x * per_square
        if square_width < chimney_dim.x * 2:
            return Result(
                error="The x-dimension of the chimney can't be greater than the center-square"
            )

        nb_seg = ceil(square_width / msh_sz)
        square_width = msh_sz * nb_seg
        partition = self._create_base(
            sketcher, center, reactor_dim, chimney_dim, square_width
        )

        print(self._geompy.CheckShape(partition))

        direction = self._geompy.MakeVectorDXDYDZ(0, 0, 1)
        solid = self._geompy.MakePrismVecH(partition, direction, reactor_dim.y)
        solid = self._geompy.MakeGlueFaces(solid, 1e-6)

        face_chimney = self._geompy.GetFaceNearPoint(
            solid, self._geompy.MakeVertex(center.x, center.y, center.z + reactor_dim.y)
        )
        chimney = self._geompy.MakePrismVecH(face_chimney, direction, chimney_dim.y)

        reactor = self._geompy.MakePartition([solid, chimney])
        reactor = self._geompy.MakeGlueFaces(reactor, 1e-6)

        faces = self._geompy.SubShapeAllSortedCentres(
            reactor, self._geompy.ShapeType["FACE"]
        )
        print("Solid created !")
        print(f"Number of faces : {len(faces)}")
        print()

        print("Creation of the groups...")
        groups = self._create_group(reactor, center, reactor_dim, chimney_dim).unwrap()
        print("Done !")
        print()

        return Result(
            value=ReactorGeometry(
                geometry=reactor,
                groups=groups,
                reactor_dim=reactor_dim,
                chimney_dim=chimney_dim,
                per_square=per_square,
                mesh_size=msh_sz,
            )
        )

    def mesh(self, geometry: ReactorGeometry) -> Result:
        if geometry.geometry is None:
            return Result(error="Geometry has not yet been created")

        mesh = self._smesh.Mesh(geometry.geometry)

        mesh.Segment().NumberOfSegments(1)

        square_width = geometry.reactor_dim.x * geometry.per_square
        nb_seg = ceil(square_width / geometry.mesh_size)
        #
        #        vertex = self._geompy.MakeVertex(square_width/2, 0, 0)
        #        edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertex)
        #        algo = mesh.Segment(edge)
        #        algo.NumberOfSegments(nb_seg)
        #        algo.Propagation()
        #
        #        vertex = self._geompy.MakeVertex(0, square_width/2, 0)
        #        edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertex)
        #        algo = mesh.Segment(edge)
        #        algo.NumberOfSegments(nb_seg)
        #        algo.Propagation()
        #
        #        circle_size = geometry.reactor_dim.x - (geometry.reactor_dim.x * geometry.per_square) / 2
        #        dr = (square_width / 2) * geometry.mesh_size
        #        nb_seg = ceil(circle_size / dr)
        #        on_line_pos = 1.1 * ((geometry.reactor_dim.x * geometry.per_square) / 2)
        #        vertex = self._geompy.MakeVertex(on_line_pos, on_line_pos, 0)
        #        edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertex)
        #        algo = mesh.Segment(edge)
        #        algo.NumberOfSegments(nb_seg)
        #        algo.Propagation()
        #
        #        nb_seg = ceil(geometry.reactor_dim.y / dr)
        #        vertex = self._geompy.MakeVertex(
        #            geometry.reactor_dim.x, geometry.reactor_dim.x, geometry.reactor_dim.y / 2
        #        )
        #        edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertex)
        #        algo = mesh.Segment(edge)
        #        algo.NumberOfSegments(nb_seg)
        #        algo.Propagation()

        edges = self._geompy.SubShapeAllSortedCentres(
            geometry.geometry, self._geompy.ShapeType["EDGE"]
        )

        def is_vertical(edge):
            [v1, v2] = self._geompy.SubShapeAllSortedCentres(
                edge, self._geompy.ShapeType["VERTEX"]
            )
            p1 = self._geompy.PointCoordinates(v1)
            p2 = self._geompy.PointCoordinates(v2)
            return abs(p1[0] - p2[0]) < 1e-9

        def is_horizontal(edge):
            [v1, v2] = self._geompy.SubShapeAllSortedCentres(
                edge, self._geompy.ShapeType["VERTEX"]
            )
            p1 = self._geompy.PointCoordinates(v1)
            p2 = self._geompy.PointCoordinates(v2)
            return abs(p1[1] - p2[1]) < 1e-6

        vertical_edges = [e for e in edges if is_vertical(e)]

        if vertical_edges:
            for edge in vertical_edges:
                length = self._geompy.BasicProperties(edge)[0]
                nb_seg = ceil(length / geometry.mesh_size)
                algo = mesh.Segment(edge)
                algo.NumberOfSegments(nb_seg)
                algo.Propagation()

        horizontal_edges = [e for e in edges if is_horizontal(e)]

        if horizontal_edges:
            for edge in horizontal_edges:
                length = self._geompy.BasicProperties(edge)[0]
                nb_seg = ceil(length / geometry.mesh_size)
                algo = mesh.Segment(edge)
                algo.NumberOfSegments(nb_seg)
                algo.Propagation()

        mesh.Quadrangle()
        # mesh.Hexahedron()

        mesh.GroupOnGeom(geometry.groups[0], "Inlet", SMESH.FACE)
        mesh.GroupOnGeom(geometry.groups[1], "Outlet", SMESH.FACE)
        mesh.GroupOnGeom(geometry.groups[2], "Wall", SMESH.FACE)

        if not mesh.Compute():
            return Result(error="Error when computing mesh")

        return Result(
            value=ReactorMesh(
                mesh=mesh,
                radius=geometry.reactor_dim.x,
                height=geometry.reactor_dim.y,
                per_square=geometry.per_square,
                geompy=self._geompy,
            )
        )
