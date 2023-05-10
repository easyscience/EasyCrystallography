from __future__ import annotations

__author__ = "github.com/wardsimon"
__version__ = "0.1.0"

from typing import TYPE_CHECKING

from crysvue.visual import UnitCell as _UnitCell
from crysvue.visual import Atoms as _Atoms
from crysvue.visual.axes import XYZAxis
from crysvue.visual.axes import ABCAxis as _ABCAxis

from vispy.visuals.transforms import MatrixTransform

if TYPE_CHECKING:
    from easyCrystallography.Components.Lattice import Lattice
    from easyCrystallography.Components.Site import PeriodicAtoms


class UnitCell(_UnitCell):
    def __init__(self, lattice: Lattice, extent=(1, 1, 1), center=None, color=(0.5, 0.5, 0.5, 1)):
        super().__init__(extent, center, color)
        self.transform = MatrixTransform()
        self.transform.matrix[:3, :3] = lattice.matrix


class Atoms(_Atoms):
    def __init__(self, atoms: PeriodicAtoms, extent=(1, 1, 1), center=None, **kwargs):
        lattice = atoms.lattice
        atoms = [[atom.specie.number, atom.fract_coords] for atom in atoms]
        spacegroup_str = lattice.spacegroup.symmetry_xyz
        super().__init__(atoms, spacegroup_str, extent, center, **kwargs)
        self.transform = MatrixTransform()
        self.transform.matrix[:3, :3] = lattice.matrix


class ABCAxis(_ABCAxis):
    def __init__(self, lattice: Lattice, **kwargs):
        lattice_matrix = lattice.matrix
        super().__init__(lattice_matrix, **kwargs)