from gladier.client import GladierClient
# This is a HACK to enable glaider logging
import gladier.tests
from pprint import pprint

from flows.gather_plot_ingest_flow import flow_definition as gather_plot_ingest_flow

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
