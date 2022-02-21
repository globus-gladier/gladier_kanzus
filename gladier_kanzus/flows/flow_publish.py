from gladier import generate_flow_definition, utils
from gladier_kanzus.flows.base_flow import BaseClient

from gladier_kanzus.tools.dials_plot_hist import dials_plot_hist

@generate_flow_definition(modifiers={
    'tar': {'endpoint': 'funcx_endpoint_non_compute'},
    'publish_gather_metadata': {'WaitTime': 240, 'payload': '$.SsxGatherData.details.result[0].pilot'},
})


class PublishFlow(BaseClient):
    containers = {
            utils.name_generation.get_funcx_function_name(dials_plot_hist): {
                'container_type': 'singularity',
                'location': '/eagle/APSDataAnalysis/SSX/containers/dials_v4.simg',
        }
    }
    globus_group = 'e31ed13f-e9e0-11e9-bbd0-0a8c64af9bb2'
    gladier_tools = [
        'gladier_kanzus.tools.gather_data.SSXGatherData',
        'gladier_tools.posix.tar.Tar',
        'gladier_kanzus.tools.plot.SSXPlot',
        'gladier_kanzus.tools.plot.DialsPlotHist',
        'gladier_tools.publish.Publish',
    ]
