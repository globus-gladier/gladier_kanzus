import datetime
from gladier import GladierBaseTool

from .create_phil import funcx_create_phil
from .dials_stills import funcx_stills_process
from .plot import ssx_plot
from .publish import ssx_publish
from .gather_data import ssx_gather_data
from .xy_search import xy_search
from .xy_plot import xy_plot

__all__ = ['CreatePhil','DialsStills','SSXGatherData','SSXPlot',
           'SSXPublish', 'XYSearch', 'XYPlot']


class CreatePhil(GladierBaseTool):
    flow_definition = None
    required_input = []
    funcx_functions = [
        funcx_create_phil
    ]

class DialsStills(GladierBaseTool):
    flow_definition = None
    required_input = []
    funcx_functions = [
        funcx_stills_process
    ]

class SSXGatherData(GladierBaseTool):
    flow_definition = None
    required_input = []
    funcx_functions = [
        ssx_gather_data
    ]

class SSXPlot(GladierBaseTool):
    flow_definition = None
    required_input = []
    funcx_functions = [
        ssx_plot
    ]

class SSXPublish(GladierBaseTool):
    flow_definition = None
    required_input = []
    funcx_functions = [
        ssx_publish
    ]

class XYSearch(GladierBaseTool):
    flow_definition = None
    required_input = []
    funcx_functions = [
        xy_search
    ]

class XYPlot(GladierBaseTool):
    flow_definition = None
    required_input = []
    funcx_functions = [
        xy_plot
    ]


class SSXGatherData(GladierBaseTool):

    flow_definition = {
      'Comment': 'Gather port-dials data for plot generation and upload',
      'StartAt': 'SSXPlot',
      'States': {
        'SSXPlot': {
          'Comment': 'Gather port-dials data for plot generation and upload',
          'Type': 'Action',
          'ActionUrl': 'https://api.funcx.org/automate',
          'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
          'ExceptionOnActionFailure': False,
          'Parameters': {
              'tasks': [{
                'endpoint.$': '$.input.funcx_endpoint_non_compute',
                'func.$': '$.input.ssx_gather_data_funcx_id',
                'payload.$': '$.input',
              }]
          },
          'ResultPath': '$.SSXGatherData',
          'WaitTime': 600,
          'End': True
        }
      }
    }

    flow_input = {
        'trigger_name': '/projects/APSDataAnalysis/nick/SSX/S9/nsp10nsp16/K/Kaleidoscope_processing',
        'metadata': {
            "description": "Automated data processing.",
            "creators": [{"creatorName": "Kanzus"}],
            "publisher": "Automate",
            "subjects": [{"subject": "SSX"}],
            "publicationYear": str(datetime.datetime.now().year),
        }
    }

    required_input = [
        'trigger_name',
    ]

    funcx_functions = [
        ssx_gather_data
    ]


class SSXPlot(GladierBaseTool):

    flow_definition = {
      'Comment': 'Plot SSX data',
      'StartAt': 'SSXPlot',
      'States': {
        'SSXPlot': {
          'Comment': 'Upload to petreldata, ingest to SSX search index',
          'Type': 'Action',
          'ActionUrl': 'https://api.funcx.org/automate',
          'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
          'ExceptionOnActionFailure': False,
          'Parameters': {
              'tasks': [{
                'endpoint.$': '$.input.funcx_endpoint_non_compute',
                'func.$': '$.input.ssx_plot_funcx_id',
                'payload.$': '$.input',
            }]
          },
          'ResultPath': '$.SSXPlot',
          'WaitTime': 600,
          'End': True
        }
      }
    }

    flow_input = {}

    required_input = []

    funcx_functions = [
        ssx_plot
    ]


class SSXPublish(GladierBaseTool):

    flow_definition = {
      'Comment': 'Run Pilot and upload the result to search + petreldata',
      'StartAt': 'SSXPilot',
      'States': {
        'SSXPilot': {
          'Comment': 'Upload to petreldata, ingest to SSX search index',
          'Type': 'Action',
          'ActionUrl': 'https://api.funcx.org/automate',
          'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
          'ExceptionOnActionFailure': False,
          'Parameters': {
              'tasks': [{
                'endpoint.$': '$.input.funcx_endpoint_non_compute',
                'func.$': '$.input.ssx_pilot_funcx_id',
                'payload.$': '$.input',
            }]
          },
          'ResultPath': '$.SSXPilot',
          'WaitTime': 600,
          'End': True
        }
      }
    }

    flow_input = {}

    required_input = []

    funcx_functions = [
        ssx_publish
    ]

