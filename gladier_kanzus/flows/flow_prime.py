from gladier import GladierBaseClient, generate_flow_definition


@generate_flow_definition
class PrimeFlow(GladierBaseClient):
    gladier_tools = [
        'gladier_kanzus.tools.Prime',
        'gladier_kanzus.tools.TransferPrime',
    ]
    