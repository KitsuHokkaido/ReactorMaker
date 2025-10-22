import salome

salome.salome_init_without_session()

from salome.geom import geomBuilder


class ReactorGeometry:
    def __init__(self, geometry, radius, height, per_square):
        self._geompy = geomBuilder.New()

        self._geometry = geometry
        self._radius = radius
        self._height = height
        self._per_square = per_square

    @property
    def geometry(self):
        return self._geometry

    @property
    def radius(self):
        return self._radius

    @property
    def height(self):
        return self._height

    @property
    def per_square(self):
        return self._per_square

    def export_to(self, filename: str) -> bool:
        if self._geometry is None:
            raise ValueError("Geometry has not yet been created")

        self._geompy.ExportVTK(self._geometry, filename)

        return True
