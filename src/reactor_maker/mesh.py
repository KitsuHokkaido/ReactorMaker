class ReactorMesh:
    def __init__(self, mesh, radius, height, per_square):
        self._mesh = mesh
        self._radius = radius
        self._height = height
        self._per_square = per_square

    @property
    def mesh(self):
        return self._mesh

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
        if self._mesh is None:
            raise ValueError("Mesh has not yet been created")

        self._mesh.ExportSTL(filename)

        return True
