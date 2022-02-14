from gladier import GladierBaseClient, generate_flow_definition



@generate_flow_definition(modifiers={
    'publish_gather_metadata': {'WaitTime': 240, 'payload': '$.SsxGatherData.details.result[0].pilot'},
})
class StillsFlow(GladierBaseClient):
    globus_group = 'e31ed13f-e9e0-11e9-bbd0-0a8c64af9bb2'
    gladier_tools = [
        'gladier_kanzus.tools.CreatePhil',
        'gladier_kanzus.tools.DialsStills',
        'gladier_kanzus.tools.SSXGatherData',
        'gladier_kanzus.tools.SSXPlot',
        'gladier_tools.publish.Publish',
        'gladier_kanzus.tools.TransferProc'
        ]

