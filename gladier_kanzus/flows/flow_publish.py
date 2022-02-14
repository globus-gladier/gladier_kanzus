from gladier import GladierBaseClient, generate_flow_definition



@generate_flow_definition(modifiers={
    'tar': {'endpoint': 'funcx_endpoint_non_compute'},
    'publish_gather_metadata': {'WaitTime': 240, 'payload': '$.SsxGatherData.details.result[0].pilot'},
})
class PublishFlow(GladierBaseClient):
    globus_group = 'e31ed13f-e9e0-11e9-bbd0-0a8c64af9bb2'
    gladier_tools = [
        'gladier_kanzus.tools.gather_data.SSXGatherData',
        'gladier_tools.posix.tar.Tar',
        'gladier_kanzus.tools.plot.SSXPlot',
        'gladier_tools.publish.Publish',
        'gladier_kanzus.tools.TransferProc'
    ]
