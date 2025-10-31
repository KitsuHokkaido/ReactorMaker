import argparse
from pathlib import Path

from .engine import ReactorMaker
from .vector import vector3, vector2

from typing import Union, Tuple


def pars_arg():
    parser = argparse.ArgumentParser(
        prog="reactor-maker",
        description="Create and mesh a reactor",
    )

    parser.add_argument(
        "-c",
        "--center",
        nargs=3,
        type=float,
        metavar=('X', 'Y', 'Z'),
        default=[0, 0, 0],
        help="Center position of the reactor (x, y, z). Default: 0 0 0",
    )

    parser.add_argument(
        "-rd",
        "--reactord",
        nargs=2,
        type=float,
        metavar=('R', 'H'),
        required=True,
        help="Reactor dimensions : (R, H) : (radius, height)",
    )

    parser.add_argument(
        "-cd",
        "--chimneyd",
        nargs=2,
        type=float,
        metavar=('R', 'H'),
        required=True,
        help="Chimney/Smokestack dimensions : (R, H) : (radius, height)",
    )

    parser.add_argument(
        "-p",
        "--per_square_curve",
        nargs=2,
        type=personnalized_per_square_constraint,
        metavar=('S', 'C'),
        default=[0.5, 0.1],
        help="Size of the square in the center of the reactor, and the curvature of the edges. Fraction of the radius. Default: (0.5, 0.1)",
    )

    parser.add_argument(
        "-m",
        "--meshing",
        required=True,
        type=float,
        help="Size characteristics of a reactor mesh",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Output directory. Default: current directory",
    )

    parser.add_argument(
        "-++",
        "--optimize",
        type=int,
        default=0,
        help="Try to optimize the meshing. 0 : no optimization. 1 : optimization",
    )

    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1.0")

    return parser.parse_args()


def personnalized_per_square_constraint(value: Union[str, float, int]) -> float:
    try:
        float(value)
    except:
        raise argparse.ArgumentTypeError(f"{value} must be a float")

    fvalue = float(value)

    if not (0 < fvalue < 1):
        raise argparse.ArgumentTypeError(f"{value} must be between 0 and 1")

    return fvalue


def main() -> None:
    args = pars_arg()

    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}")
    print(f"Creating reactor with:")
    print(f"  Center: {args.center}")
    print(f"  Radius: {args.reactord[0]}")
    print(f"  Height: {args.reactord[1]}")
    print(f"  (per square, per curvature): {args.per_square_curve}")
    print("Creating chimney with:")
    print(f"  Radius: {args.chimneyd[0]}")
    print(f"  Height: {args.chimneyd[1]}")
    print()

    optimize = args.optimize != 0

    maker = ReactorMaker()

    geometry = maker.create_geometry(
        center=vector3(*args.center),
        reactor_dim=vector2(*args.reactord),
        chimney_dim=vector2(*args.chimneyd),
        per_square=args.per_square_curve[0],
        mesh_size=args.meshing,
        per_curvature=args.per_square_curve[1],
        optimize=optimize,
    ).unwrap()

    if geometry.export_to(f"{args.output}/geometry.stl"):
        print("File succesfully saved !")
    mesh = maker.mesh(geometry, optimize).unwrap()

    if mesh.export_to(f"{args.output}/mesh.unv"):
        print("File succesfully saved !")


if __name__ == "__main__":
    main()
