from gladier import GladierBaseClient, generate_flow_definition, utils
from gladier_kanzus.flows.flow_base import BaseClient

from gladier_kanzus.tools.prime import dials_prime


@generate_flow_definition
class PrimeFlow(BaseClient):
    globus_group = 'e31ed13f-e9e0-11e9-bbd0-0a8c64af9bb2'

    containers = {
            utils.name_generation.get_funcx_function_name(dials_prime): {
                'container_type': 'singularity',
                'location': '/eagle/APSDataAnalysis/SSX/containers/dials_v3.simg',
        }
    }
    
    gladier_tools = [
        'gladier_kanzus.tools.Prime',
        'gladier_kanzus.tools.TransferPrime',
    ]
    
