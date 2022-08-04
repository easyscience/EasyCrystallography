__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import param
import panel as pn

from easyCrystallography.graphics import NGLViewer
from easyCrystallography.graphics.panel.lattice import ParameterLattice
from easyCrystallography.graphics.panel.spacegroup import ParameterSpaceGroup
from easyCrystallography.graphics.panel.atoms import ParameterAtoms

from easyCrystallography.Structures.Phase import Phase

def create_Phase_panel(phase):
    """
    Creates a panel for a Phase object.
    """

    class ParameterPhase(pn.viewable.Viewer):
        p_instance = param.ClassSelector(class_=phase.__class__, instantiate=True)
        _pn_l = param.ClassSelector(class_=ParameterLattice, instantiate=True)
        _pn_a = param.ClassSelector(class_=ParameterAtoms, instantiate=True)
        _pn_sg = param.ClassSelector(class_=ParameterSpaceGroup, instantiate=True)
        structure = param.ClassSelector(class_=NGLViewer, instantiate=True)

        def __init__(self, phase_obj):
            opts = {}
            if phase_obj is not None:
                opts['p_instance'] = phase_obj
                opts['_pn_l'] = ParameterLattice(phase_obj.cell)
                opts['_pn_a'] = ParameterAtoms(phase_obj.atoms)
                opts['_pn_sg'] = ParameterSpaceGroup(phase_obj.spacegroup)
                cif = phase_obj.cif
                dis_ops = {'representation': 'ball+stick'}
                if len(phase_obj.atoms) == 0:
                    dis_ops['representation'] = 'unitcell'
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
                opts['structure'] = NGLViewer(object=cif, extension='cif', background="#F7F7F7",
                                              sizing_mode='stretch_both',
                                              **dis_ops)

            super().__init__(name="Phase Panel", **opts)
            self._layout = pn.Column(self.structure, pn.Row(self._pn_l, self._pn_sg, self._pn_a))

        @param.depends('p_instance', watch=True)
        def _upadate_objs(self):
            self._pn_l = ParameterLattice(self.p_instance.cell)
            self._pn_a = ParameterAtoms(self.p_instance.atoms)
            self._pn_sg = ParameterSpaceGroup(self.p_instance.spacegroup)
            self._update_structure()

        @param.depends('_pn_l.param', '_pn_a.param', '_pn_sg.param', 'structure.param', watch=True)
        def _update_structure(self):
            cif = self.p_instance.cif
            if len(self.p_instance.atoms) == 0:
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
            self.structure.object = cif

        def view(self):
            wb = pn.WidgetBox('###' + self.name, pn.Row(self._layout, pn.Column(self._pn_l.gen_str, self._pn_sg.gen_str,
                                                                                sizing_mode='stretch_width')))
            return wb

        def __panel__(self):
            return pn.WidgetBox('###' + self.name, self._layout)
    return ParameterPhase(phase)



