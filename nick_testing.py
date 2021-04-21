from gladier.client import GladierClient
# This is a HACK to enable glaider logging
import gladier.tests
from pprint import pprint


class SSXReprocessing(GladierClient):
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
    gladier_tools = [
        'gladier_kanzus.tools.publish.SSXPilot',
        # 'gladier_kanzus.tools.plot.SSXPlot',
    ]

    # flow_definition = 'gladier_kanzus.tools.plot.SSXPlot'
    flow_definition = 'gladier_kanzus.tools.publish.SSXPilot'


if __name__ == '__main__':
    flow_input = {
        'input': {
            # NEEDED FOR PLOTS
            'input_files': '/projects/APSDataAnalysis/nick/SSX/S9/nsp10nsp16/K/Kaleidoscope_15_22100.cbf',
            'input_range': '00000..22100',

            # NEEDED FOR PUBLISH
            'aps_data': '/gdata/dm/SBC/SSX-DATA/ssx9/',
            'chip': 'Kaleidoscope',
            'experiment_number': '15',
            'protein': 'nsp10nsp16',
            'run_name': 'S9',
            'trigger_name': '/projects/APSDataAnalysis/nick/SSX/S9/nsp10nsp16/K/Kaleidoscope_15_22016.cbf',

            # NEEDED FOR NICK
            'funcx_endpoint_non_compute': '0a162a09-8bd9-4dd9-b046-0bfd635d38a7',
            'funcx_endpoint_compute': '37e6099f-e9e7-4817-ac68-4afcd78d8221',
        }
    }
    re_cli = SSXReprocessing()
    corr_flow = re_cli.start_flow(flow_input=flow_input)
    action_id = corr_flow['action_id']
    re_cli.progress(action_id)
    pprint(re_cli.get_status(action_id))
