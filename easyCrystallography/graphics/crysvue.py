from __future__ import annotations

__author__ = "github.com/wardsimon"
__version__ = "0.1.0"

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from easyCrystallography.Components.Lattice import Lattice
    from easyCrystallography.Components.Site import PeriodicAtoms


from crysvue.visual import VisualBase
from crysvue.logic.atoms import AtomsLogic
from crysvue.logic.unit_cell import UnitCellLogic
from crysvue.logic.axes import AxesLogic


class UnitCell(VisualBase, UnitCellLogic):
    _LABEL = 'UnitCell'

    def __init__(self, lattice: Lattice, extent=(1, 1, 1), center=None, color=(0.5, 0.5, 0.5, 1)):
        VisualBase.__init__(self, extent, center, color, frac_to_abc=lattice.matrix)


class Atoms(VisualBase, AtomsLogic):
    _LABEL = 'Atoms'

    def __init__(self, atoms: PeriodicAtoms, extent=(1, 1, 1), center=None, **kwargs):
        lattice = atoms.lattice
        spacegroup_str = lattice.spacegroup.symmetry_xyz
        positions, sizes, colors, symmetry_str = self._from_atom_name([atom.fract_coords for atom in atoms],
                                                                      [atom.label.raw_value for atom in atoms],
                                                                      spacegroup_str)
        VisualBase.__init__(self, positions, sizes, colors, symmetry_str,
                         extent=extent, center=center, frac_to_abc=lattice.matrix, **kwargs)


class ABCAxis(VisualBase, AxesLogic):
    _LABEL = 'ABCAxis'

    def __init__(self, lattice: Lattice, **kwargs):
        lattice_matrix = lattice.matrix
        VisualBase.__init__(self, lattice_matrix, **kwargs)