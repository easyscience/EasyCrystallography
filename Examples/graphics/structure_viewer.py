#  SPDX-FileCopyrightText: 2023 easyCrystallography contributors <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022-2023  Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>

from vispy import app

from easyCrystallography.Components.Lattice import Lattice, PeriodicLattice
from easyCrystallography.Components.Site import PeriodicAtoms, Site
from easyCrystallography.Components.SpaceGroup import SpaceGroup

from crysvue.canvases.canvas import CrystalCanvas
from crysvue.interface.easyCrystallography import UnitCell, Atoms, ABCAxis


lattice = Lattice(4, 4, 8, 90, 90, 120)
space_group = SpaceGroup.from_int_number(194)
site1 = Site('H', 'H', 1, 0., 0., 0.)
site2 = Site('Fe', 'Fe', 1, 0.4, 0.25, 0.4)

atoms = PeriodicAtoms('test', site1, site2,
                      lattice=PeriodicLattice.from_lattice_and_spacegroup(lattice, space_group))


canvas = CrystalCanvas(keys='interactive', show=True)

extent = (1, 1, 1)
cell_visual = UnitCell(lattice, extent=extent)
atom_visual = Atoms(atoms, extent=extent)

axis_visual = ABCAxis(lattice)

canvas.add_element('unit_cell', cell_visual)
canvas.add_element('atoms', atom_visual)
canvas.add_element('axes', axis_visual)


if __name__ == '__main__':
    app.run()
