from gladier.client import GladierClient
# This is a HACK to enable glaider logging
import gladier.tests
from pprint import pprint

gather_plot_ingest_flow = {
      'Comment': 'Gather data for plotting ad publish',
      'StartAt': 'SSXGatherData',
      'States': {
        'SSXGatherData': {
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
          'Next': 'SSXPlot',
        },
        'SSXPlot': {
          'Comment': 'Plot the pack-man image',
          'Type': 'Action',
          'ActionUrl': 'https://api.funcx.org/automate',
          'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
          'ExceptionOnActionFailure': False,
          'Parameters': {
              'tasks': [{
                'endpoint.$': '$.input.funcx_endpoint_non_compute',
                'func.$': '$.input.ssx_plot_funcx_id',
                'payload': {
                    'xdim.$': '$.SSXGatherData.details.result.metadata.user_input.x_num_steps',
                    'ydim.$': '$.SSXGatherData.details.result.metadata.user_input.y_num_steps',
                    'int_indices.$': '$.SSXGatherData.details.result.int_indices',
                    'plot_filename.$': '$.SSXGatherData.details.result.plot_filename',
                }
            }]
          },
          'ResultPath': '$.SSXPlot',
          'WaitTime': 600,
          'Next': 'SSXPublish',
        },
        'SSXPublish': {
              'Comment': 'Publish data on petrel and globus search',
              'Type': 'Action',
              'ActionUrl': 'https://api.funcx.org/automate',
              'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
              'ExceptionOnActionFailure': False,
              'Parameters': {
                  'tasks': [{
                      'endpoint.$': '$.input.funcx_endpoint_non_compute',
                      'func.$': '$.input.ssx_publish_funcx_id',
                      'payload': {
                          'metadata.$': '$.SSXGatherData.details.result.metadata',
                          'upload_dir.$': '$.SSXGatherData.details.result.upload_dir',
                      }
                  }]
              },
              'ResultPath': '$.SSXPublish',
              'WaitTime': 600,
              'End': True
          }
      }
    }


class SSXPlotAndPublish(GladierClient):
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
    gladier_tools = [
        'gladier_kanzus.tools.SSXGatherData',
        'gladier_kanzus.tools.SSXPlot',
        'gladier_kanzus.tools.SSXPublish',
    ]

    flow_definition = gather_plot_ingest_flow


if __name__ == '__main__':
    flow_input = {
        'input': {
            'trigger_name': '/eagle/APSDataAnalysis/SSX/S12/PDL1/B/Bounce_7_37400.cbf',

            # NEEDED FOR NICK
            'funcx_endpoint_non_compute': '0a162a09-8bd9-4dd9-b046-0bfd635d38a7',
            'funcx_endpoint_compute': '37e6099f-e9e7-4817-ac68-4afcd78d8221',
        }
    }
    re_cli = SSXPlotAndPublish()
    corr_flow = re_cli.start_flow(flow_input=flow_input)
    action_id = corr_flow['action_id']
    re_cli.progress(action_id)
    pprint(re_cli.get_status(action_id))
