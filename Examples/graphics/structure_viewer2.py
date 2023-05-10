#  SPDX-FileCopyrightText: 2023 easyCrystallography contributors <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022-2023  Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>

from vispy import app
import numpy as np
from easyCrystallography.Components.Lattice import Lattice, PeriodicLattice
from easyCrystallography.Components.Site import PeriodicAtoms, Site
from easyCrystallography.Components.SpaceGroup import SpaceGroup
from easyCrystallography.Components.Spin import Spin

from crysvue.canvases.canvas import CrystalCanvas
from crysvue.visual.components import Arrow3D
from easyCrystallography.graphics.crysvue import UnitCell, Atoms, ABCAxis


lattice = Lattice(5, 5, 5, 90, 90, 90)
space_group = SpaceGroup.from_int_number(202)
s = Spin(s_x=0, s_y=0, s_z=1)
site = Site('Fe', 'Fe', 1., 0., 0., 0., spin=s)

atoms = PeriodicAtoms('test', site,
                      lattice=PeriodicLattice.from_lattice_and_spacegroup(lattice, space_group))


canvas = CrystalCanvas(keys='interactive', show=True)

extent = (1, 1, 1)
cell_visual = UnitCell(lattice, extent=extent)
atom_visual = Atoms(atoms, extent=extent)

axis_visual = ABCAxis(lattice)

spin = {0: [0, 0, 1]}

for atom in atoms:
    s = atom.spin
    images = s.images(space_group)
    points = space_group.get_orbit(atom.fract_coords)
    for image, point in zip(images, points):
        arrow = Arrow3D(np.matmul(lattice.matrix, point - [0.5, 0.5, 0.5]), image.matrix, color='red', radius=0.1,
                        length=1, centered=True, parent=canvas.view.scene)

canvas.add_element('unit_cell', cell_visual)
canvas.add_element('atoms', atom_visual)
canvas.add_element('axes', axis_visual)


if __name__ == '__main__':
    app.run()
