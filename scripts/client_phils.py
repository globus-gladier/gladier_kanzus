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

##hacking over container
from tools.dials_stills import funcx_stills_process as stills_cont
'cont_dir': '/home/rvescovi/.funcx/containers/'}
container_name = "dials_v3.simg"
dials_cont_id = fxc.register_container(location=os.path.join(conf['cont_dir'],container_name), container_type='singularity')
stills_cont_fxid = fxc.register_function(stills_cont, container_uuid=dials_cont_id)
##

##
conf = {'endpoint': '8f2f2eab-90d2-45ba-a771-b96e6d530cad',
        'local_endpoint': '8f2f2eab-90d2-45ba-a771-b96e6d530cad',
        'data_dir': '/eagle/APSDataAnalysis/SSX/S12/BurnPaper/A',
        'proc_dir': '/eagle/APSDataAnalysis/SSX/S12/BurnPaper/A_test'
        }

run_name = '04_21_proc_v2'
proc_range = "{00001..00500}"

flow_input = {
    "input": {
        #Processing variables
        "proc_dir": conf['proc_dir']+'/'+run_name,

        #Dials specific variables.
        "input_files": f"{conf['data_dir']}/Bounce_7_{proc_range}.cbf", 
        "input_range": proc_range[1:-1],
        "nproc": 10,
        "beamx": "-214.400",
        "beamy": "218.200",

        # funcX endpoints
        "funcx_ep": conf['endpoint'],
        "funcx_local_ep": conf['local_endpoint'],

        # container hack for stills
        "stills_cont_fxid": stills_cont_fxid
    }
}
##

phils_flow = phils_client.start_flow(flow_input=flow_input)
