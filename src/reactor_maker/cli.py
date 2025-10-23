import argparse
from pathlib import Path

from .core import ReactorMaker
from .vector.vector import vector3, vector2

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
        "-rd", "--reactord",
        nargs=2,
        type=float,
        metavar=('R', 'H'),
        required=True,
        help="Reactor dimensions : (R, H) : (radius, height)"
    )

    parser.add_argument(
        "-cd", "--chimneyd",
        nargs=2,
        type=float,
        metavar=('R', 'H'),
        required=True,
        help="Chimney/Smokestack dimensions : (R, H) : (radius, height)"
    )

    parser.add_argument(
        "-p", "--per_square",
        type=float,
        default=0.5,
        help="Size of the square in the center of the reactor. Fraction of the radius. Default: 0.5"
    )

    parser.add_argument(
        "-m", "--meshing",
        required=True,
        type=float,
        help="Size characteristics of a reactor mesh"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=".",
        help="Output directory. Default: current directory"
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
    print(f"  Radius: {args.reactord[0]}")
    print(f"  Height: {args.reactord[1]}")
    print(f"  Per square: {args.per_square}")
    print("Creating chimney with:")
    print(f"  Radius: {args.chimneyd[0]}")
    print(f"  Height: {args.chimneyd[1]}")
    print()

    maker = ReactorMaker() 

    geometry = maker.create_geometry(
        center=vector3(*args.center),
        reactor_dim=vector2(*args.reactord), 
        chimney_dim=vector2(*args.chimneyd), 
        per_square=args.per_square, 
        mesh_size=args.meshing
    ).unwrap()

    if geometry.export_to(f"{args.output}/geometry.stl"):
        print("File succesfully saved !")

    mesh = maker.mesh(geometry).unwrap()

    if mesh.export_to(f"{args.output}/mesh.unv"):
        print("File succesfully saved !")

    #mesh.save_as(f"{args.output}/mesh.hdf")


if __name__ == "__main__":
    main()
