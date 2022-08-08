__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import param
import panel as pn

from easyCore.Objects.ObjectClasses import BaseObj
from easyCrystallography.graphics import NGLViewer
from easyCrystallography.graphics.panel.lattice import ParameterLattice
from easyCrystallography.graphics.panel.spacegroup import ParameterSpaceGroup
from easyCrystallography.graphics.panel.atoms import ParameterAtoms


class ParameterPhase(pn.viewable.Viewer):
    phase_obj = param.ClassSelector(class_=BaseObj, instantiate=True)
    _pn_l = param.ClassSelector(class_=ParameterLattice, instantiate=True)
    _pn_a = param.ClassSelector(class_=ParameterAtoms, instantiate=True)
    _pn_sg = param.ClassSelector(class_=ParameterSpaceGroup, instantiate=True)
    cif_string = param.String(default='')

    def __init__(self, phase_obj):
        opts = {
            'phase_obj': phase_obj,
            '_pn_l': ParameterLattice(phase_obj.cell),
            '_pn_a': ParameterAtoms(phase_obj.atoms),
            '_pn_sg': ParameterSpaceGroup(phase_obj.spacegroup)
        }
        dis_ops = {'representation': 'ball+stick'}
        super().__init__(name="Phase Panel", **opts)
        self.structure = NGLViewer(object='', extension='cif', background="#F7F7F7", sizing_mode='stretch_both', **dis_ops)
        self._layout = pn.Column(self.structure, pn.WidgetBox('###Parameters', pn.Row(self._pn_l, self._pn_sg, self._pn_a)))
        self._cif_editor = pn.widgets.TextAreaInput(value=self.cif_string, height=400, sizing_mode='stretch_both')
        self._update_structure()

    @param.depends('phase_obj', watch=True)
    def _update_objs(self):
        with param.parameterized.batch_call_watchers(self):
            self._pn_l.lattice_obj = self.phase_obj.cell
            self._pn_a.atoms_obj = self.phase_obj.atoms
            self._pn_sg.spacegroup_obj = self.phase_obj.spacegroup
        self._update_structure()

    @param.depends('_pn_l.param', '_pn_a.param', '_pn_sg.param',  watch=True)
    def _update_structure(self):
        base_cif = self.phase_obj.cif
        cif = base_cif
        if len(self.phase_obj.atoms) == 0:
            cif += """
                    loop_
                     _atom_site_label
                     _atom_site_type_symbol
                     _atom_site_fract_x
                     _atom_site_fract_y
                     _atom_site_fract_z
                     _atom_site_occupancy
                      H  H   0.0   0.0   0.0   1.0
                    """
        else:
            cif = self.phase_obj.reduced_symmetry().cif
        self.cif_string = base_cif
        self.structure.object = cif

    @param.depends('cif_string')
    def cif_string_panel(self):
        self._cif_editor.value = self.cif_string
        return self._cif_editor

    def view(self):
        wb = pn.WidgetBox('###' + self.name, pn.Row(self._layout, pn.Column(self._pn_l.gen_str, self._pn_sg.gen_str,
                                                                            sizing_mode='stretch_width'),
                                                    sizing_mode='stretch_width'),
                          sizing_mode='stretch_width')
        return wb

    def __panel__(self):
        return pn.WidgetBox('###' + self.name, self._layout, sizing_mode='stretch_both')



