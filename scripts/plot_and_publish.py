from pprint import pprint
from gladier import GladierBaseClient, generate_flow_definition
import gladier_kanzus.logging  # noqa


@generate_flow_definition(modifiers={
    'ssx_plot': {'payload': '$.SsxGatherData.details.result[0].plot'},
    'publish_gather_metadata': {'WaitTime': 120, 'payload': '$.SsxGatherData.details.result[0].pilot'},
})
class SSXPlotAndPublish(GladierBaseClient):
    gladier_tools = [
        # These two tools are not functional yet.
        # 'gladier_kanzus.tools.CreatePhil',
        # 'gladier_kanzus.tools.DialsStills',
        'gladier_kanzus.tools.gather_data.SSXGatherData',
        'gladier_kanzus.tools.plot.SSXPlot',
        'gladier_tools.publish.Publish',
    ]


if __name__ == '__main__':

    upload_dir = '/projects/APSDataAnalysis/nick/SSX/S13/LYSO/A/A_images'
    flow_input = {
        'input': {
            'trigger_name': '/projects/APSDataAnalysis/nick/SSX/S13/LYSO/A/Avalon_13_00025.cbf',
            'proc_dir': '/projects/APSDataAnalysis/nick/SSX/S13/LYSO/A/a_processing',
            'upload_dir': upload_dir,

            'pilot': {
                # This is the directory which will be published to petrel
                'dataset': upload_dir,
                'index': '5e63bb08-5b39-4a02-86f3-44cec03e8bc0',
                'project': 'ssx',
                'source_globus_endpoint': '08925f04-569f-11e7-bef8-22000b9a448b',
                # Extra groups can be specified here. The SSX Admin group will always
                # be provided automatically.
                'groups': []
            },
        }
    }
    re_cli = SSXPlotAndPublish()
    corr_flow = re_cli.run_flow(flow_input=flow_input)
    action_id = corr_flow['action_id']
    re_cli.progress(action_id)
    pprint(re_cli.get_status(action_id))
