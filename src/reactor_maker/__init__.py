"""
Reactor Maker
=============

A library for creating and meshing reactors.

Basic usage:
    >>> from reactor_maker import ReactorMaker, vector3
    >>> maker = ReactorMaker()
    >>> geometry = maker.create_geometry(center=vector3(0, 0, 0), radius=20)
"""

from .core import ReactorMaker
from .vector.vector import vector3, vector2

__version__ = "0.1.0"
__all__ = ["ReactorMaker", "vector3", "vector2"]
