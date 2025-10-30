import salome

salome.salome_init_without_session()

from salome.geom import geomBuilder


class ReactorGeometry:
    def __init__(
        self,
        geometry,
        groups,
        reactor_dim,
        chimney_dim,
        per_square,
        mesh_size,
        square_width,
    ):
        self._geompy = geomBuilder.New()

        self._geometry = geometry
        self._reactor_dim = reactor_dim
        self._chimney_dim = chimney_dim
        self._per_square = per_square
        self._groups = groups
        self._mesh_size = mesh_size
        self._square_width = square_width

    @property
    def geometry(self):
        return self._geometry

    @property
    def reactor_dim(self):
        return self._reactor_dim

    @property
    def chimney_dim(self):
        return self._chimney_dim

    @property
    def per_square(self):
        return self._per_square

    @property
    def groups(self):
        return self._groups

    @property
    def mesh_size(self):
        return self._mesh_size

    @property
    def square_width(self):
        return self._square_width

    def export_to(self, filename: str) -> bool:
        if self._geometry is None:
            raise ValueError("Geometry has not yet been created")

        self._geompy.ExportSTL(self._geometry, filename)

        return True
