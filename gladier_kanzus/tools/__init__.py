from gladier.defaults import GladierDefaults as GladierBaseTool

from .create_phil import funcx_create_phil
from .dials_stills import funcx_stills_process
from .plot import ssx_plot
from .publish import ssx_publish
from .gather_data import ssx_gather_data

__all__ = ['CreatePhil','DialsStills']


class CreatePhil(GladierBaseTool):
    flow_definition = None
    required_input = []
    # funcx_endpoints = dict()
    funcx_functions = [
        funcx_create_phil
    ]

class DialsStills(GladierBaseTool):
    flow_definition = None
    required_input = []
    # funcx_endpoints = dict()
    funcx_functions = [
        funcx_stills_process
    ]

class SSXGatherData(GladierBaseTool):
    flow_definition = None
    required_input = []
    # funcx_endpoints = dict()
    funcx_functions = [
        ssx_gather_data
    ]
    
class SSXPlot(GladierBaseTool):
    flow_definition = None
    required_input = []
    # funcx_endpoints = dict()
    funcx_functions = [
        ssx_plot
    ]

class SSXPublish(GladierBaseTool):
    flow_definition = None
    required_input = []
    # funcx_endpoints = dict()
    funcx_functions = [
        ssx_publish
    ]

# DialsVersion = GladierBaseTool()

# Pilot = GladierBaseTool()

# Prime = GladierBaseTool()

# Primalisys = GladierBaseTool()
