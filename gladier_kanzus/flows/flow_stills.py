from gladier import GladierBaseClient, generate_flow_definition



@generate_flow_definition(modifiers={
    'create_phil': {'endpoint': 'funcx_endpoint_non_compute'},
    'stills_process': {'WaitTime':3600}
})
class StillsFlow(GladierBaseClient):
    globus_group = 'e31ed13f-e9e0-11e9-bbd0-0a8c64af9bb2'
    gladier_tools = [
        'gladier_kanzus.tools.CreatePhil',
        'gladier_kanzus.tools.DialsStills',
        'gladier_kanzus.tools.TransferProc',
    ]
