__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import param
import panel as pn
from easyCore.Objects.ObjectClasses import BaseObj
from easyCore.Objects.Groups import BaseCollection

class ParameterAtom(pn.viewable.Viewer):
    atom_obj = param.ClassSelector(class_=BaseObj, doc="Atom object")
    label = param.String('H')
    specie = param.String('H')
    x = param.Number(default=0, bounds=(-1, 1))
    y = param.Number(default=0, bounds=(-1, 1))
    z = param.Number(default=0, bounds=(-1, 1))
    occupancy = param.Number(default=1, bounds=(0, None))

    _params = [('label', 'label'), ('specie', 'specie'), ('x', 'fract_x'), ('y', 'fract_y'), ('z', 'fract_z'), ('occupancy', 'occupancy')]

    def __init__(self, atom):

        self._label = pn.widgets.TextInput(name='', value=atom.label.raw_value, width=75)
        self._specie = pn.widgets.TextInput(name='', value=atom.specie.raw_value, width=75)
        self._x = pn.widgets.FloatInput(value=atom.fract_x.raw_value,
                                         start=self.param['x'].bounds[0], end=self.param['x'].bounds[1], width=50, margin=(5, 5))
        self._y = pn.widgets.FloatInput(value=atom.fract_y.raw_value,
                                         start=self.param['y'].bounds[0], end=self.param['y'].bounds[1], width=50, margin=(5, 5))
        self._z = pn.widgets.FloatInput(value=atom.fract_z.raw_value,
                                         start=self.param['z'].bounds[0], end=self.param['z'].bounds[1], width=50, margin=(5, 5))
        self._occupancy = pn.widgets.FloatInput(name='', value=atom.occupancy.raw_value,
                                                 start=self.param['occupancy'].bounds[0], width=50)

        super().__init__(name="Atom Panel",
                         label=atom.label.raw_value,
                         specie=atom.specie.raw_value,
                         x=atom.x.raw_value,
                         y=atom.y.raw_value,
                         z=atom.z.raw_value,
                         occupancy=atom.occupancy.raw_value,
                         atom_obj=atom
                         )
        self._layout = pn.Column(pn.Row(
            pn.WidgetBox('Label', self._label),
            pn.WidgetBox('Specie', self._specie),
            pn.WidgetBox('XYZ', pn.Row(self._x, self._y, self._z), align=('start', 'end'), margin=5),
            pn.WidgetBox('Occupancy', self._occupancy),  sizing_mode='stretch_width')
        )
        self._heading = pn.pane.Markdown(f'##{self.label} Editor')
        self._sync_widgets()

    @param.depends('label', watch=True)
    def _sync_heading(self):
        self._heading.name = f'##{self.label} Editor'

    @param.depends('atom_obj', watch=True)
    def _update_from_atom(self):
        with param.parameterized.discard_events(self):
            for par in self._params:
                val = getattr(self.atom_obj, par[1])
                setattr(self, '_' + par[0] + '.value', val)
                setattr(self, par[0], val.value)

    @param.depends(*[par[0] for par in _params], watch=True)
    def _sync_widgets(self):
        with param.parameterized.batch_call_watchers(self):
            for par in self._params:
                val = getattr(self, par[0])
                setattr(self.atom_obj, par[1], val)
                setattr(self, '_' + par[0] + '.value', val)

    @param.depends(*['_' + par[0] + '.value' for par in _params], watch=True)
    def _sync_params(self):
        with param.parameterized.batch_call_watchers(self):
            for par in self._params:
                val = getattr(self, '_' + par[0])
                setattr(self.atom_obj, par[1], val.value)
                setattr(self, par[0], val.value)

    def __panel__(self):
        return pn.WidgetBox(f'##{self.label} Editor', self._layout, sizing_mode='stretch_width')


class ParameterAtoms(pn.viewable.Viewer):

    _atoms_dict = param.Dict()
    atoms_obj = param.ClassSelector(class_=BaseCollection, doc="Atoms object")

    def __init__(self, atoms):
        atoms_list_widget = pn.widgets.Select(name='Available Atoms',
                                              options=[atom.label.raw_value for atom in atoms],
                                              sizing_mode='stretch_width')

        self._atoms_widget = atoms_list_widget
        cv = pn.Row(sizing_mode='stretch_width')
        self._current_view = cv,
        add = pn.widgets.Button(name='Add Atom', button_type='primary', sizing_mode='stretch_width')
        self._add = add,
        remove = pn.widgets.Button(name='Remove Atom', button_type='danger', sizing_mode='stretch_width')
        self._remove = remove,

        super().__init__(name="Atoms Panel",
                         _atoms_dict={atom.label.raw_value: ParameterAtom(atom) for atom in atoms},
                         atoms_obj=atoms)

        self._add[0].on_click(self.add_atom_button_callback)
        self._remove[0].on_click(self.rem_atom_button_callback)

        self._update_current_atom()
        self._layout = pn.Column(
                 pn.Column(pn.Row(self._atoms_widget), pn.Row(self._add[0], self._remove[0], sizing_mode='stretch_width')),
                 self._current_view[0],
             )

    @param.depends('atoms_obj', watch=True)
    def _update_from_atoms(self):
        with param.parameterized.discard_events(self):
            self._atoms_dict = {atom.label.raw_value: ParameterAtom(atom) for atom in self.atoms_obj}
            self._atoms_widget.options = [atom.label.raw_value for atom in self.atoms_obj]
            if len(self._atoms_widget.options) > 0:
                self._atoms_widget.value = self._atoms_widget.options[0]
            else:
                self._atoms_widget.value = ''

    @param.depends('_atoms_widget.value', watch=True)
    def _update_current_atom(self):
        atom = self._atoms_dict.get(self._atoms_widget.value, False)
        self._current_view[0].objects = []
        if atom:
            self._current_view[0].objects = [atom]

    def add_atom_button_callback(self, event):
        this_atom = self.atoms_obj._SITE_CLASS(label=f'H{self._add[0].clicks}', specie='H')
        self.atoms_obj.append(this_atom)
        with param.parameterized.batch_call_watchers(self):
            self._atoms_dict[this_atom.label.raw_value] = ParameterAtom(this_atom)
            self._atoms_widget.options = list(self._atoms_dict.keys())

    def rem_atom_button_callback(self, event):

        atom_label = self._atoms_widget.value
        all_atom_labels = self._atoms_widget.options
        index = all_atom_labels.index(atom_label)

        with param.parameterized.batch_call_watchers(self):
            del all_atom_labels[index]
            if len(all_atom_labels) > 0:
                self._atoms_widget.value = all_atom_labels[0]
            else:
                self._atoms_widget.value = ''
            self._atoms_widget.options = all_atom_labels

            self._atoms_dict.pop(atom_label)
        del self.atoms_obj[atom_label]

    def __panel__(self):
        return pn.WidgetBox('#####' + self.name, self._layout)
