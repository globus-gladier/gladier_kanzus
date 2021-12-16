from gladier import GladierBaseClient, generate_flow_definition


@generate_flow_definition
class BlockTransferFlow(GladierBaseClient):
    globus_group = 'e31ed13f-e9e0-11e9-bbd0-0a8c64af9bb2'
    gladier_tools = [
        'gladier_kanzus.tools.TransferOut',
    ]


