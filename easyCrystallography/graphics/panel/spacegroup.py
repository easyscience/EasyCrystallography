__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import param
import panel as pn
from easyCore.Objects.ObjectClasses import BaseObj
from easyCrystallography.Symmetry.tools import SpacegroupInfo


class ParameterSpaceGroup(pn.viewable.Viewer):
    spacegroup_obj = param.ClassSelector(class_=BaseObj, instantiate=True)
    sg_HM_name = param.String()
    sg_setting = param.Selector(None)

    _params = [('sg_HM_name', 'space_group_HM_name'), ('sg_setting', 'setting')]

    def __init__(self, spacegroup_obj):

        self.sg_system = pn.widgets.Select(name='System',
                                           options=[s[0].upper() + s[1:] for s in SpacegroupInfo.get_all_systems()])
        self._sg_HM_name = pn.widgets.Select(name='HM Name', groups={})

        super().__init__(name="Spacegroup Panel",
                         sg_HM_name=spacegroup_obj.hermann_mauguin,
                         sg_setting=spacegroup_obj.setting_str,
                         spacegroup_obj=spacegroup_obj)
        self._layout = pn.Column(self.sg_system, self._sg_HM_name, self.param.sg_setting)
        self._sync_widgets()

    @param.depends('spacegroup_obj', watch=True)
    def _update_from_spacegroup(self):
        with param.parameterized.discard_events(self):
            self.sg_HM_name = self.spacegroup_obj.hermann_mauguin
            self.sg_setting = self.spacegroup_obj.setting_str
        with param.parameterized.discard_events(self.sg_system):
            new_system = self.spacegroup_obj.crystal_system
            self.sg_system.value = new_system[0].upper() + new_system[1:]
        with param.parameterized.discard_events(self._sg_HM_name):
            self._sg_HM_name.groups = {
                str(this_system): list(
                    {par.split(':')[0] for par in SpacegroupInfo.get_compatible_HM_from_int(this_system) if
                     '(' not in par})
                for this_system in list(SpacegroupInfo.get_ints_from_system(self.sg_system.value.lower()))
            }
            self._sg_HM_name.value = self.spacegroup_obj.hermann_mauguin

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
        self.spacegroup_obj.space_group_HM_name = self.sg_HM_name
        settings = self.spacegroup_obj.settings
        # if settings:
        self.param.sg_setting.objects = settings
        #     self.param.sg_setting. = True
        # else:
        #     self.param.sg_setting.viewable = False

    @param.depends('sg_setting', watch=True)
    def _sync_system(self):
        self.spacegroup_obj.setting = self.sg_setting

    @param.depends('sg_HM_name', 'sg_setting')
    def gen_str(self):
        s = ['Spacegroup Details\n']
        for par in self._params:
            val = getattr(self, par[0])
            if val:
                s.append(f'{par[1]}:\t{val}')
        s.append(f'Reference Setting:\t{self.spacegroup_obj.is_reference_setting}')
        s.append(f'Operators:\t{self.spacegroup_obj.symmetry_xyz}')
        return pn.pane.Str('\n'.join(s))

    def __panel__(self):
        return pn.WidgetBox('#####' + self.name, self._layout)

    def view(self):
        view = self._layout
        return pn.WidgetBox('###' + self.name, pn.Row(view, self.gen_str))
