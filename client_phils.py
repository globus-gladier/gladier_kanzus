#from gladier import GladierBaseClient
from gladier.client import GladierClient as GladierBaseClient




from flows.phils_beta_raf import flow_definition as flow_phil

class KanzusPhilsClient(GladierBaseClient):
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'

    gladier_tools = [
        'tools.CreatePhil',
        'tools.DialsStills',
    ]
    flow_definition = flow_phil

phils_client = KanzusPhilsClient()

##
conf = {'endpoint': '8f2f2eab-90d2-45ba-a771-b96e6d530cad',
        'local_endpoint': '8f2f2eab-90d2-45ba-a771-b96e6d530cad',
        'data_dir': '/eagle/APSDataAnalysis/SSX/S12/BurnPaper/A',
        'proc_dir': '/eagle/APSDataAnalysis/SSX/S12/BurnPaper/A_test'
        }

run_name = '04_21_proc_v2'
proc_range = "{00001..00050}"

flow_input = {
    "input": {
        #Processing variables
        "proc_dir": conf['proc_dir']+'/'+run_name,

        #Dials specific variables.
        "input_files": f"{conf['data_dir']}/Arise_3_{proc_range}.cbf", 
        "input_range": proc_range[1:-1],
        "nproc": 10,
        "beamx": "-214.400",
        "beamy": "218.200",

        # funcX endpoints
        "funcx_ep": conf['endpoint'],
        "funcx_local_ep": conf['local_endpoint'],
    }
}
##

phils_flow = phils_client.start_flow(flow_input=flow_input)
