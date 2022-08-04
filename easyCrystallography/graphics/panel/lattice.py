__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


import param
import panel as pn
from easyCrystallography.graphics import NGLViewer
pn.extension("ngl_viewer")


class ParameterLattice(pn.viewable.Viewer):
    a = param.Number(default=3., bounds=(0, None), doc="Cell length a", label="Length a")
    b = param.Number(default=3., bounds=(0, None), doc="Cell length b", label="Length b")
    c = param.Number(default=3., bounds=(0, None), doc="Cell length c", label="Length c")
    alpha = param.Number(default=90., bounds=(0, 180), doc="Cell angle alpha", label="Angle alpha")
    beta = param.Number(default=90., bounds=(0, 180), doc="Cell angle beta", label="Angle beta")
    gamma = param.Number(default=90., bounds=(0, 180), doc="Cell angle gamma", label="Angle gamma")

    _parms = [('a', 'length_a'), ('b', 'length_b'), ('c', 'length_c'), ('alpha', 'angle_alpha'), ('beta', 'angle_beta'),
              ('gamma', 'angle_gamma')]

    def __init__(self, lat):
        self._a = pn.widgets.FloatSlider(name=self.param['a'].label, value=self.param['a'].default,
                                         start=self.param['a'].bounds[0], end=30)
        self._b = pn.widgets.FloatSlider(name=self.param['b'].label, value=self.param['b'].default,
                                         start=self.param['b'].bounds[0], end=30)
        self._c = pn.widgets.FloatSlider(name=self.param['c'].label, value=self.param['c'].default,
                                         start=self.param['c'].bounds[0], end=30)
        self._alpha = pn.widgets.FloatSlider(name=self.param['alpha'].label, value=self.param['alpha'].default,
                                             start=self.param['alpha'].bounds[0], end=self.param['alpha'].bounds[1])
        self._beta = pn.widgets.FloatSlider(name=self.param['beta'].label, value=self.param['beta'].default,
                                            start=self.param['beta'].bounds[0], end=self.param['beta'].bounds[1])
        self._gamma = pn.widgets.FloatSlider(name=self.param['gamma'].label, value=self.param['gamma'].default,
                                             start=self.param['gamma'].bounds[0], end=self.param['gamma'].bounds[1])
        self._lat = lat
        super().__init__(name="Lattice Panel",
                         a=lat.length_a.raw_value,
                         b=lat.length_b.raw_value,
                         c=lat.length_c.raw_value,
                         alpha=lat.angle_alpha.raw_value,
                         beta=lat.angle_beta.raw_value,
                         gamma=lat.angle_gamma.raw_value
                         )
        self._layout = pn.Column(self._a, self._b, self._c, self._alpha, self._beta, self._gamma)
        self.structure = NGLViewer(object="", extension='cif', background="#F7F7F7", representation='unitcell')
        self._sync_widgets()
        self._update_structure()

    @param.depends(*[par[0] for par in _parms], watch=True)
    def _sync_widgets(self):
        for par in self._parms:
            val = getattr(self, par[0])
            setattr(self._lat, par[1], val)
            setattr(self, '_' + par[0] + '.value', val)

    @param.depends(*['_' + par[0] + '.value' for par in _parms], watch=True)
    def _update_structure(self):
        cif_obj = f"""
        data_CellViewer

        _space_group_name_H-M_alt   'P1'

        _cell_length_a       {self._a.value}
        _cell_length_b       {self._b.value}
        _cell_length_c       {self._c.value}
        _cell_angle_alpha   {self._alpha.value}
        _cell_angle_beta    {self._beta.value}
        _cell_angle_gamma   {self._gamma.value}

        loop_
         _atom_site_label
         _atom_site_type_symbol
         _atom_site_fract_x
         _atom_site_fract_y
         _atom_site_fract_z
         _atom_site_occupancy
          H  H   0.0   0.0   0.0   1.0
        """
        self.structure.object = cif_obj

    @param.depends(*['_' + par[0] + '.value' for par in _parms], watch=True)
    def _sync_params(self):
        for par in self._parms:
            val = getattr(self, '_' + par[0])
            setattr(self._lat, par[1], val.value)
            setattr(self, par[0], val.value)

    @param.depends(*['_' + par[0] + '.value' for par in _parms])
    def gen_str(self):
        s = ['Lattice Details\n']
        for par in self._parms:
            val = getattr(self, par[0])
            s.append(f'{par[1]}:\t{val}')
        s.append(f'\nVolume\t{self._lat.volume}')
        return pn.pane.Str('\n'.join(s))

    def __panel__(self):
        return pn.WidgetBox('###' + self.name, self._layout)

    def view(self):
        view = self._layout
        return pn.WidgetBox('###' + self.name, pn.Row(view, self.gen_str))

    def full_view(self):
        view = self._layout
        return pn.WidgetBox('###' + self.name, pn.Row(view, self.structure))
