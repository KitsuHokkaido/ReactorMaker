# Reactor Maker

Create and mesh reactor geometries.

## Features 

 - **Parametric reactor design** - Define reactors with simple parameters 
 - **3D geometry generation** - Create reactor geometries
 - **Automatic meshing** - Generate high-quality meshing
 - **CLI & GUI** - Use it from command line or graphical interface

## Quick Start
### Installation 

```bash
git clone https://github.com/KitsuHokkaido/ReactorMaker.git
cd ReactorMaker

conda create -n reactor-maker-env
conda activate reactor-maker

pip install -e .

```

### Basic Usage 

Before executing any of this following command, don't forget to activate your salome environnement by this command : (if salome is in your PATH) 

```bash
salome context
```

#### Command Line

Simple example with required parameters

```bash
reactor-maker -rd 20 100 -cd 6 10 -m 2 
```

#### Gui 

```bash
reactor-maker-gui
```

## Documentation

For detailed documentation, see : 

- [Installation Guide](docs/installation.md)
- [User Guide](docs/user-guide/README.md)
- [API Reference](docs/api-reference/README.md)
- [Examples](docs/user-guide/examples.md)

## Example 

### Creating a simple reactor using the API

```python
from .engine import ReactorMaker
from .vector import vector3, vector2

maker = ReactorMaker()

geometry = maker.create_geometry(
    center=vector3(0, 0, 0), # position of your reactor
    reactor_dim=vector2(20, 100), # (radius, height)
    chimney_dim=vector2(6, 10), # (width, height)
    per_square=0.9, # size of the central square meshing, fraction of the radius
    mesh_size=2, # characteritics mesh size
).unwrap()

mesh = maker.mesh(geometry, False).unwrap() # mesh the geometry with option optimized to False

geometry.export_to(f"$HOME/Desktop/geometry.stl") # specify where you wish to save it
mesh.export_to(f"$HOME/Desktop/mesh.unv") 
```
