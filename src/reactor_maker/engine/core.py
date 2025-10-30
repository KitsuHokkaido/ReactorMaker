import salome

salome.salome_init_without_session()

import GEOM, SMESH
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder

from pathlib import Path
from math import pi, ceil, log, sqrt

from ..error import Result
from ..vector import vector3, vector2

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
        base = self._geompy.MakeVertex(
            center.x, center.y, center.z + reactor_dim.y + chimney_dim.y
        )
        direction = self._geompy.MakeVectorDXDYDZ(0, 0, 1)
        items = self._geompy.GetShapesOnPlaneWithLocationIDs(
            geometry, self._geompy.ShapeType["FACE"], direction, base, GEOM.ST_ON
        )
        self._geompy.UnionIDs(outlet, items)

        wall = self._geompy.CreateGroup(geometry, self._geompy.ShapeType["FACE"])
        pts = [
            vector3(center.x + radius, center.y, center.z + height / 2),
            vector3(center.x - radius, center.y, center.z + height / 2),
            vector3(center.x, center.y + radius, center.z + height / 2),
            vector3(center.x, center.y - radius, center.z + height / 2),
            vector3(
                center.x + chimney_dim.x / 2,
                center.y,
                center.z + height + chimney_dim.y / 2,
            ),
            vector3(
                center.x - chimney_dim.x / 2,
                center.y,
                center.z + height + chimney_dim.y / 2,
            ),
            vector3(
                center.x,
                center.y + chimney_dim.x / 2,
                center.z + height + chimney_dim.y / 2,
            ),
            vector3(
                center.x,
                center.y - chimney_dim.x / 2,
                center.z + height + chimney_dim.y / 2,
            ),
        ]

        vertices = [self._geompy.MakeVertex(pt.x, pt.y, pt.z) for pt in pts]

        faces = [
            self._geompy.GetFaceNearPoint(geometry, vertice) for vertice in vertices
        ]
        self._geompy.UnionList(wall, faces)

        base = self._geompy.MakeVertex(center.x, center.y, center.z + reactor_dim.y)
        direction = self._geompy.MakeVectorDXDYDZ(0, 0, 1)
        items = self._geompy.GetShapesOnPlaneWithLocationIDs(
            geometry, self._geompy.ShapeType["FACE"], direction, base, GEOM.ST_ON
        )
        top_center_face = self._geompy.GetFaceNearPoint(geometry, base)
        top_face_id = self._geompy.GetSubShapeID(geometry, top_center_face)

        items.remove(top_face_id)

        self._geompy.UnionIDs(wall, items)
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
        meshing_square = self._geompy.MakeGlueEdges(meshing_square, 1e-7)

        partition = self._geompy.MakePartition([disk], [meshing_square, *lines])
        partition = self._geompy.MakeGlueEdges(partition, 1e-7)

        return partition

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
        if square_width < 0.8 * chimney_dim.x:
            return Result(
                error="The x-dimension of the chimney can't be greater than the center-square"
            )

        nb_seg = ceil(square_width / msh_sz)
        square_width = msh_sz * nb_seg
        partition = self._create_base(
            sketcher, center, reactor_dim, chimney_dim, square_width
        )

        print(
            f"Quality of the meshing : {"Ok" if self._geompy.CheckShape(partition) else "No"}"
        )

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
                square_width=square_width,
            )
        )

    def mesh(self, geometry: ReactorGeometry, optimize:bool) -> Result:
        if geometry.geometry is None:
            return Result(error="Geometry has not yet been created")

        all_edges = self._geompy.SubShapeAllSortedCentres(
            geometry.geometry, self._geompy.ShapeType["EDGE"]
        )

        mesh = self._smesh.Mesh(geometry.geometry)

        mesh.Segment().NumberOfSegments(1)

        points = [
            vector3(geometry.chimney_dim.x / 2, 0, 0),
            vector3(geometry.chimney_dim.x / 2, geometry.chimney_dim.x / 2 + 1, 0),
            vector3(geometry.chimney_dim.x / 2, -geometry.chimney_dim.x / 2 - 1, 0),
            vector3(0, geometry.chimney_dim.x / 2, 0),
            vector3(geometry.chimney_dim.x / 2 + 1, geometry.chimney_dim.x / 2, 0),
            vector3(-geometry.chimney_dim.x / 2 - 1, geometry.chimney_dim.x / 2, 0),
            vector3(
                geometry.reactor_dim.x,
                geometry.reactor_dim.x,
                geometry.reactor_dim.y / 2,
            ),
            vector3(
                geometry.chimney_dim.x,
                geometry.chimney_dim.x,
                geometry.reactor_dim.y + geometry.chimney_dim.y / 2,
            ),
            vector3(geometry.reactor_dim.x, 0, 0),
            vector3(0, geometry.reactor_dim.x, 0),
            vector3(-geometry.reactor_dim.x, 0, 0),
            vector3(0, -geometry.reactor_dim.x, 0),
        ]

        nb_seg_tot = 0
        for i, point in enumerate(points):
            vertice = self._geompy.MakeVertex(point.x, point.y, point.z)
            edge = self._geompy.GetEdgeNearPoint(geometry.geometry, vertice)

            length = self._geompy.BasicProperties(edge)[0]
            nb_seg = ceil(length / geometry.mesh_size)

            if i >= 0 and i <= 2:
                nb_seg_tot += nb_seg

            if i >= 8:
                nb_seg = nb_seg_tot

            algo = mesh.Segment(edge)
            algo.NumberOfSegments(nb_seg)
            algo.Propagation()

        on_line_pos = (
            geometry.square_width / 2 + (1 / 2 ** (1 / 2)) * geometry.reactor_dim.x
        ) / 2
        point = vector3(on_line_pos, on_line_pos, 0)
        edge = self._find_egde_by_geometry(all_edges, point).unwrap()

        algo = mesh.Segment(edge)
        if optimize:
            edge_length_min, ratio = self._get_max_length(
                geometry.reactor_dim.x, geometry.square_width, geometry.mesh_size
            )
            algo.GeometricProgression(edge_length_min, ratio)
        else:
            length = self._geompy.BasicProperties(edge)[0]
            nb_seg = ceil(length / geometry.mesh_size)
            algo.NumberOfSegments(nb_seg)
        algo.Propagation()

        mesh.Quadrangle()
        mesh.Hexahedron()

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

    def _get_max_length(self, R, square_width, mesh_size):
        N_theta = ceil(square_width / mesh_size)
        #r0 = sqrt(2) * (square_width / 2)
        r0 = (mesh_size * 4 * N_theta) / (2 * pi)
        q = 1 + (2 * pi) / (4 * N_theta)

        def r_i(i):
            return r0 * (1 + (2 * pi) / (4 * N_theta)) ** i

        N = log(R / r0) / log(1 + (2 * pi) / (4 * N_theta))

        dr_min = r_i(1) - r_i(0)
        dr_max = r_i(N) - r_i(N - 1) 

        return dr_min, q

    def _find_egde_by_geometry(self, all_edges, center_pt: vector3, tol=1e-1) -> Result:
        for edge in all_edges:
            vertices = self._geompy.ExtractShapes(
                edge, self._geompy.ShapeType["VERTEX"]
            )

            coords1 = self._geompy.PointCoordinates(vertices[0])
            coords2 = self._geompy.PointCoordinates(vertices[1])
            coords = [abs(coords1[i] + coords2[i]) / 2 for i in range(3)]

            if (
                abs(coords[0] - center_pt.x) < tol
                and abs(coords[1] - center_pt.y) < tol
                and abs(coords[2] - center_pt.z) < tol
            ):

                return Result(value=edge)

        return Result(error="No edge find")
