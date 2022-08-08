__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import panel as pn
import tempfile
from easyCrystallography.graphics.panel.phase import ParameterPhase


def create_dashboard(phase):

    Phase = getattr(phase, '__old_class__', phase.__class__)
    panel_phase = ParameterPhase(phase)

    def save_cif():
        from io import StringIO
        f = StringIO(panel_phase.cif_string)
        f.seek(0)
        return f

    save_cif_button = pn.widgets.FileDownload(filename='phase.cif', button_type='success',
                                              callback=save_cif, auto=False, embed=False,
                                              name='Right click to save as CIF')
    update_cif_button = pn.widgets.Button(name='Update', button_type='primary')
    cif_panel = pn.Column(panel_phase.cif_string_panel, pn.Row(update_cif_button,
                                                               pn.Spacer(sizing_mode='stretch_width'),
                                                               save_cif_button,
                                                               sizing_mode='stretch_width'), sizing_mode='stretch_both')

    def load_string(event):
        if file_input.value is None:
            pn.pane.Alert('## Alert\nA cif file needs to se selected')
            return
        panel_phase.phase_obj = Phase.from_cif_string(cif_panel.value)
    update_cif_button.on_click(load_string)

    bootstrap = pn.template.BootstrapTemplate(title='Structure Editor')
    tabs = pn.Tabs(('Structure', panel_phase),
                   ('CIF', cif_panel))
    bootstrap.main.append(tabs)
    file_input = pn.widgets.FileInput(accept='.cif')
    load_cif_button = pn.widgets.Button(name='Load', button_type='primary')
    def load_file(event):
        if file_input.value is None:
            pn.pane.Alert('## Alert\nA cif file needs to se selected')
            return
        panel_phase.phase_obj = Phase.from_cif_string(file_input.value.decode('utf-8'))
    load_cif_button.on_click(load_file)

    load_cif_wiget = pn.WidgetBox('###Load cif file', pn.Column(file_input, load_cif_button))
    display_widget = pn.WidgetBox('###Cell display', panel_phase.structure.param.representation)

    bootstrap.sidebar.append(load_cif_wiget)
    bootstrap.sidebar.append(display_widget)
    return bootstrap


if __name__ == '__main__':
    from easyCrystallography.Structures.Phase import Phase
    phase = Phase('panel')
    dashboard = create_dashboard(phase)
    pn.serve({
        'structure': dashboard,
    }, title={'structure': 'View and edit crystal structure'})
