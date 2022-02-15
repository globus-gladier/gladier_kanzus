from gladier import GladierBaseClient, generate_flow_definition, utils
from gladier_kanzus.flows.flow_base import BaseClient

from gladier_kanzus.tools.dials_stills import dials_stills



@generate_flow_definition(modifiers={
    'publish_gather_metadata': {'WaitTime': 240, 'payload': '$.SsxGatherData.details.result[0].pilot'},
})
class StillsFlow(BaseClient):
    globus_group = 'e31ed13f-e9e0-11e9-bbd0-0a8c64af9bb2'

    containers = {
        utils.name_generation.get_funcx_function_name(dials_stills): {
            'container_type': 'singularity',
            'location': '/eagle/APSDataAnalysis/SSX/containers/dials_v3.simg',
        }
    }
    
    gladier_tools = [
        # 'gladier_kanzus.tools.TransferOut',
        'gladier_kanzus.tools.WaitTrigger',
        'gladier_kanzus.tools.CreatePhil',
        'gladier_kanzus.tools.DialsStills',
        'gladier_kanzus.tools.SSXGatherData',
        'gladier_kanzus.tools.SSXPlot',
        'gladier_tools.publish.Publish',
        'gladier_kanzus.tools.TransferProc'
        ]

