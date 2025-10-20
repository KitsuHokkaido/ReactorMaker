import salome
salome.salome_init_without_session()

import GEOM
from salome.geom import geomBuilder
from pathlib import Path

from error.error import Result

class ReactorMaker:
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self._OUTPUT_DIR = project_root.joinpath("outputs")

        self._geompy = geomBuilder.New()

    def mesh(self):
        return Result(value="Success")

    def export_to(self, filename:str) -> bool:
        sphere = self._geompy.MakeSphereR(100)
        self._geompy.ExportVTK(sphere, f"{self._OUTPUT_DIR}/{filename}")
        return True
