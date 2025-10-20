from reactor_maker import ReactorMaker

if __name__ == "__main__":
    reactor_example = ReactorMaker()

    reactor_example.mesh()
    reactor_example.export_to("sphere.vtk")


