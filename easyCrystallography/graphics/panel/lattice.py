__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'


import param
import panel as pn
from easyCore.Objects.ObjectClasses import BaseObj


class ParameterLattice(pn.viewable.Viewer):
    lattice_obj = param.ClassSelector(class_=BaseObj, doc="Lattice object", instantiate=True)
    a = param.Number(default=3., bounds=(0, None), doc="Cell length a", label="Length a")
    b = param.Number(default=3., bounds=(0, None), doc="Cell length b", label="Length b")
    c = param.Number(default=3., bounds=(0, None), doc="Cell length c", label="Length c")
    alpha = param.Number(default=90., bounds=(0, 180), doc="Cell angle alpha", label="Angle alpha")
    beta = param.Number(default=90., bounds=(0, 180), doc="Cell angle beta", label="Angle beta")
    gamma = param.Number(default=90., bounds=(0, 180), doc="Cell angle gamma", label="Angle gamma")

    _params = [('a', 'length_a'), ('b', 'length_b'), ('c', 'length_c'), ('alpha', 'angle_alpha'), ('beta', 'angle_beta'),
               ('gamma', 'angle_gamma')]

    def __init__(self, lattice_obj):
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
        super().__init__(name="Lattice Panel",
                         a=lattice_obj.length_a.raw_value,
                         b=lattice_obj.length_b.raw_value,
                         c=lattice_obj.length_c.raw_value,
                         alpha=lattice_obj.angle_alpha.raw_value,
                         beta=lattice_obj.angle_beta.raw_value,
                         gamma=lattice_obj.angle_gamma.raw_value,
                         lattice_obj=lattice_obj
                         )
        self._layout = pn.Column(self._a, self._b, self._c, self._alpha, self._beta, self._gamma)
        self._sync_widgets()

    @param.depends('lattice_obj', watch=True)
    def _update_from_lattice(self):
        with param.parameterized.discard_events(self):
            for par in self._params:
                val = getattr(self.lattice_obj, par[1]).raw_value
                setattr(self, par[0], val)
                widget = getattr(self, '_' + par[0])
                with param.parameterized.discard_events(widget):
                    setattr(widget, 'value', val)

    @param.depends(*[par[0] for par in _params], watch=True)
    def _sync_widgets(self):
        with param.parameterized.batch_call_watchers(self):
            for par in self._params:
                val = getattr(self, par[0])
                setattr(self.lattice_obj, par[1], val)
                setattr(getattr(self, '_' + par[0]), 'value', val)

    @param.depends(*['_' + par[0] + '.value' for par in _params], watch=True)
    def _sync_params(self):
        with param.parameterized.batch_call_watchers(self):
            for par in self._params:
                val = getattr(self, '_' + par[0])
                setattr(self.lattice_obj, par[1], val.value)
                setattr(self, par[0], val.value)

    @param.depends(*['_' + par[0] + '.value' for par in _params])
    def gen_str(self):
        s = ['Lattice Details\n']
        for par in self._params:
            val = getattr(self, par[0])
            s.append(f'{par[1]}:\t{val}')
        s.append(f'\nVolume\t{self.lattice_obj.volume}')
        return pn.pane.Str('\n'.join(s))

    def __panel__(self):
        return pn.WidgetBox('#####' + self.name, self._layout)
