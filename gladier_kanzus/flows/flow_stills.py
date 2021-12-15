from gladier import GladierBaseClient, generate_flow_definition



@generate_flow_definition(modifiers={
    'create_phil': {'endpoint': 'funcx_endpoint_non_compute'},
    'stills_process': {'WaitTime':3600}
})
class StillsFlow(GladierBaseClient):
    gladier_tools = [
        'gladier_kanzus.tools.CreatePhil',
        'gladier_kanzus.tools.DialsStills',
        'gladier_kanzus.tools.TransferProc',
    ]
