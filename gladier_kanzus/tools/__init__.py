import datetime
from gladier.defaults import GladierDefaults
from gladier_kanzus.tools import gather_data, plot, publish


class SSXGatherData(GladierDefaults):

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
        gather_data.ssx_gather_data
    ]


class SSXPlot(GladierDefaults):

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
        plot.ssx_plot
    ]


class SSXPublish(GladierDefaults):

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
        publish.ssx_publish
    ]
