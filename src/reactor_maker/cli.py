from .core import ReactorMaker
from .vector.vector import vector3

def main() -> None:
    maker = ReactorMaker()

    geometry = maker.create_geometry(center=vector3(0, 0, 0), radius=20, height=100, per_square=0.5)
    mesh = maker.mesh(geometry)
    
    if maker.geo_export_to("disk.vtk", geometry):
        print("File succesfully saved !")

    if maker.mesh_export_to("disk_mesh.stl", mesh):
        print("File succesfully saved !")


if __name__ == "__main__":
    main()
