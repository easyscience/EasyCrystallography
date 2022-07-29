__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import param
import panel as pn
from easyCrystallography.Symmetry.tools import SpacegroupInfo


class ParameterSpaceGroup(pn.viewable.Viewer):
    sg_HM_name = param.String()
    sg_setting = param.Selector(None)

    _params = [('sg_HM_name', 'space_group_HM_name'), ('sg_setting', 'setting')]

    def __init__(self, this_sg):

        self.sg_system = pn.widgets.Select(name='System',
                                           options=[s[0].upper() + s[1:] for s in SpacegroupInfo.get_all_systems()])
        self._sg_HM_name = pn.widgets.Select(name='HM Name', groups={})

        super().__init__(name="Spacegroup Panel", sg_HM_name=this_sg.hermann_mauguin, sg_setting=this_sg.setting_str)
        self._sg = this_sg
        self._layout = pn.Column(self.sg_system, self._sg_HM_name, self.param.sg_setting)
        self._sync_widgets()

    @param.depends('sg_system.value', watch=True)
    def _sync_widgets(self):
        self._sg_HM_name.groups = {
            str(this_system): list(
                {par.split(':')[0] for par in SpacegroupInfo.get_compatible_HM_from_int(this_system) if '(' not in par})
            for this_system in list(SpacegroupInfo.get_ints_from_system(self.sg_system.value.lower()))
        }
        self.sg_HM_name = self._sg_HM_name.value

    @param.depends('sg_HM_name', watch=True)
    def _sync_params(self):
        self._sg_HM_name.value = self.sg_HM_name

    @param.depends('_sg_HM_name.value', watch=True)
    def _sync_name(self):
        self.sg_HM_name = self._sg_HM_name.value
        self._sg.space_group_HM_name = self.sg_HM_name
        settings = self._sg.settings
        # if settings:
        self.param.sg_setting.objects = settings
        #     self.param.sg_setting. = True
        # else:
        #     self.param.sg_setting.viewable = False

    @param.depends('sg_setting', watch=True)
    def _sync_system(self):
        self._sg.setting = self.sg_setting

    @param.depends('sg_HM_name', 'sg_setting')
    def gen_str(self):
        s = ['Spacegroup Details\n']
        for par in self._params:
            val = getattr(self, par[0])
            if val:
                s.append(f'{par[1]}:\t{val}')
        s.append(f'Reference Setting:\t{self._sg.is_reference_setting}')
        s.append(f'Operators:\t{self._sg.symmetry_xyz}')
        return pn.pane.Str('\n'.join(s), height=380, width=500)

    def __panel__(self):
        return pn.Column('###' + self.name, self._layout)

    def view(self):
        view = self._layout
        return pn.Column('###' + self.name, pn.Row(view, self.gen_str))
