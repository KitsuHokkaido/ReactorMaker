class ReactorMesh:
    def __init__(self, mesh, radius, height, per_square, geompy):
        self._mesh = mesh
        self._radius = radius
        self._height = height
        self._per_square = per_square
        self._geompy = geompy

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

        self._mesh.ExportUNV(filename)

        return True

    def save_as(self, filename:str):
        self._geompy.myStudy.SaveAs(filename, self._geompy.myStudy._get_Name(), False)

