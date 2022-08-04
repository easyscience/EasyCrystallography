__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import panel as pn
import tempfile
from easyCrystallography.Structures.Phase import Phase
from easyCrystallography.graphics.panel.phase import create_Phase_panel

phase = Phase('panel')
panel_phase = create_Phase_panel(phase)

bootstrap = pn.template.BootstrapTemplate(title='Structure Editor')
bootstrap.main.append(panel_phase.view)
file_input = pn.widgets.FileInput(accept='.cif')
load_cif_button = pn.widgets.Button(name='Load', button_type='primary')
def load_file(event):
    if file_input.value is None:
        pn.pane.Alert('## Alert\nA cif file needs to se selected')
        return
    with tempfile.TemporaryFile() as tmp:
        file_input.save(tmp.name)
        panel_phase.p_instance = Phase.from_cif_file(tmp.name)
load_cif_button.on_click(load_file)

load_cif_wiget = pn.WidgetBox('###Load cif file', pn.Column(file_input, load_cif_button))
display_widget = pn.WidgetBox('###Cell display', panel_phase.structure.param.representation)

bootstrap.sidebar.append(load_cif_wiget)
bootstrap.sidebar.append(display_widget)

# bootstrap2 = pn.template.BootstrapTemplate(title='Simulation')

pn.serve({
    'structure': bootstrap,
}, title={'structure': 'View and edit crystal structure'})
