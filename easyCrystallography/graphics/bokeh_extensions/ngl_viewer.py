__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from bokeh.core.properties import String, List
from bokeh.models import LayoutDOM


class NGLViewer(LayoutDOM):
    object = String()
    extension = String()
    representation = String()
    color_scheme = String()
    effect = String()
    custom_color_scheme = List(List(String))
    # background = String()

    __javascript__ = [
        "https://unpkg.com/ngl@2.0.0-dev.37/dist/ngl.js",
    ]

    __js_skip__ = {
        "NGL": __javascript__[:1],
    }

    __js_require__ = {
        "paths": {
            "NGL": "https://unpkg.com/ngl@2.0.0-dev.37/dist/ngl",
        },
        "exports": {"NGL": "NGL"},
    }
