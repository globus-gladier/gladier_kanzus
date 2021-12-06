from gladier import GladierBaseClient, generate_flow_definition



@generate_flow_definition(modifiers={
    'tar': {'endpoint': 'funcx_endpoint_non_compute'},
    'ssx_plot': {'payload': '$.SsxGatherData.details.result[0].plot'},
    'publish_gather_metadata': {'WaitTime': 120, 'payload': '$.SsxGatherData.details.result[0].pilot'},
})
class PlotAndPublish(GladierBaseClient):
    gladier_tools = [
        'gladier_kanzus.tools.gather_data.SSXGatherData',
        'gladier_tools.posix.tar.Tar',
        'gladier_kanzus.tools.plot.SSXPlot',
        'gladier_tools.publish.Publish',
    ]

