import argparse
from pathlib import Path

from .core import ReactorMaker
from .vector.vector import vector3

def pars_arg():
    parser = argparse.ArgumentParser(
        prog="reactor-maker",
        description="Create and mesh a reactor", 
    )

    parser.add_argument(
        "-c", "--center",
        nargs=3,
        type=float, 
        metavar=('X', 'Y', 'Z'),
        default=[0, 0, 0],
        help="Center position of the reactor (x, y, z). Default: 0 0 0"
    )

    parser.add_argument(
        "-r", "--radius",
        type=float,
        required=True,
        help="Reactor radius"
    )

    parser.add_argument(
        "-s", "--height",
        type=float,
        required=True,
        help="Reactor height"
    )

    parser.add_argument(
        "-p", "--per_square",
        type=float,
        default=0.5,
        help="Size of the square in the center of the reactor. Fraction of the radius. Default: 0.5"
    )

    parser.add_argument(
        "-m", "--meshing",
        nargs=3, 
        type=float,
        default=[0.4, 0.4, 0.4],
        metavar=('S', 'C', 'H'),
        help="Specify the fraction of the edge to mesh. S : square, C: circle, H: height. Default: 0.4 0.4 0.4"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=".",
        help="output directory. Default: current directory"
    )

    parser.add_argument(
        "-v", "--version", 
        action="version", 
        version="%(prog)s 0.1.0")


    return parser.parse_args()

def main() -> None:
    args = pars_arg()
    
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}")
    print(f"Creating reactor with:")
    print(f"  Center: {args.center}")
    print(f"  Radius: {args.radius}")
    print(f"  Height: {args.height}")
    print(f"  Per square: {args.per_square}")
    print()

    maker = ReactorMaker() 

    geometry = maker.create_geometry(
        center=vector3(*args.center),
        radius=args.radius, 
        height=args.height, 
        per_square=args.per_square
    ).unwrap()

    if geometry.export_to(f"{args.output}/geometry.vtk"):
        print("File succesfully saved !")

    mesh = maker.mesh(
        geometry, 
        square_divs=args.meshing[0], 
        circle_divs=args.meshing[1], 
        height_divs=args.meshing[2]
    ).unwrap()

    if mesh.export_to(f"{args.output}/mesh.stl"):
        print("File succesfully saved !")


if __name__ == "__main__":
    main()
