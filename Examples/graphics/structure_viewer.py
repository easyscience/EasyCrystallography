#  SPDX-FileCopyrightText: 2023 easyCrystallography contributors <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022-2023  Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>

# Import the canvas
from crysvue import Canvas
# Import standard EC classes
from easyCrystallography.Components.Lattice import Lattice, PeriodicLattice
from easyCrystallography.Components.Site import PeriodicAtoms, Site
from easyCrystallography.Components.SpaceGroup import SpaceGroup

# Import Visuals
from easyCrystallography.graphics.crysvue import UnitCell as UnitCellVisual, \
    Atoms as AtomsVisual, ABCAxis as ABCAxisVisual


canvas = Canvas(display='app')




lattice = Lattice(4, 4, 8, 90, 90, 120)
space_group = SpaceGroup.from_int_number(194)
site1 = Site('H', 'H', 1, 0., 0., 0.)
site2 = Site('Fe', 'Fe', 1, 0.4, 0.25, 0.4)

atoms = PeriodicAtoms('test', site1, site2,
                      lattice=PeriodicLattice.from_lattice_and_spacegroup(lattice, space_group))


extent = (1, 1, 1)
cell_visual = UnitCellVisual(lattice, extent=extent)
atom_visual = AtomsVisual(atoms, extent=extent)

axis_visual = ABCAxisVisual(lattice)

canvas.add_element(cell_visual)
canvas.add_element(atom_visual)
canvas.add_element(axis_visual)

canvas.run()

