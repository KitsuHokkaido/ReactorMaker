# Command-Line Interface (CLI) Guide

The `reactor-maker` command-line tool provides a quick way to generate reactor geometries and meshes.

## Basic Usage

### Minimal Command

The minimal command requires reactor and chimney dimensions, plus mesh size:

```bash
reactor-maker -rd 20 100 -cd 6 20 -m 2
```

This creates:
- A reactor with radius=20, height=100
- A chimney with radius=6, height=20
- Mesh size characteristic=2
- Output in current directory

### Full Command with Options

```bash
reactor-maker \
  -c 0 0 0 \              # Center position (x y z)
  -rd 20 100 \            # Reactor dimensions (radius height)
  -cd 6 20 \              # Chimney dimensions (width height)
  -p 0.5 \                # Per square parameter
  -m 2 \                  # Mesh size
  -++ 1 \                 # Activate the optimization of the meshing        
  -o ./outputs            # Output directory
```

## Command-Line Options

### Required Arguments

| Option | Long Form | Description | Example |
|--------|-----------|-------------|---------|
| `-rd` | `--reactord` | Reactor dimensions (radius, height) | `-rd 20 100` |
| `-cd` | `--chimneyd` | Chimney dimensions (width, height) | `-cd 6 20` |
| `-m` | `--meshing` | Mesh size characteristic | `-m 2` |

### Optional Arguments

| Option | Long Form | Description | Default |
|--------|-----------|-------------|---------|
| `-c` | `--center` | Center position (x y z) | `0 0 0` |
| `-p` | `--per_square` | Square size fraction | `0.5` |
| `-++`| `--optimize`| Optimized meshing | `0` |
| `-o` | `--output` | Output directory | `.` (current) |
| `-v` | `--version` | Show version | - |
| `-h` | `--help` | Show help | - |

## Examples

### Example 1: Basic Reactor

Create a simple reactor in the current directory:

```bash
reactor-maker -rd 15 80 -cd 5 15 -m 1.5
```

Output files:
- `./geometry.stl` - Reactor geometry
- `./mesh.unv` - Finite element mesh

### Example 2: Custom Center Position

Create a reactor centered at (10, 20, 30):

```bash
reactor-maker -c 10 20 30 -rd 20 100 -cd 6 20 -m 2
```

### Example 3: Activate optimized meshing option 

Option --optimize is activate for 1 and deactivate for 0

```bash
reactor-maker -rd 20 100 -cd 6 20 -m 2 -++ 1
```

## Next Steps

- Learn about the [GUI interface](gui.md)
- See more [examples](examples.md)
- Check the [API reference](../api-reference/index.md) for Python usage
