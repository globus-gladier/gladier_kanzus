from gladier import GladierBaseClient



class Kanzus_Phils_Client(GladierBaseClient):
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
    gladier_tools = [
        'gladier_tools.xpcs.EigenCorr',
        'gladier_tools.xpcs.ApplyQmap',
    ]
    flow_definition = 'flows.phils_beta_raf'


conf = {'endpoint': '8f2f2eab-90d2-45ba-a771-b96e6d530cad',
        'local_endpoint': '8f2f2eab-90d2-45ba-a771-b96e6d530cad',
        'data_dir': '/eagle/APSDataAnalysis/SSX/S12/BurnPaper/A',
        'proc_dir': '/eagle/APSDataAnalysis/SSX/S12/BurnPaper/A_test'
        }

run_name = 'test1'

flow_input = {
    "input": {
        #Processing variables
        "proc_dir": os.path.join(conf['proc_dir'],run_name),

        #Dials specific variables.
        "input_files": f"{conf['data_dir']}/levin_29/Levin_29_{proc_range}.cbf", 
        "input_range": proc_range[1:-1],
        "nproc": 10,
        "beamx": "-214.400",
        "beamy": "218.200",

        #Dials funcX functions
        "create_phil_fxid": create_phil_fxid,
        "stills_fxid": stills_fxid,
        "plot_fxid": plot_ssx_fxid,

        # funcX endpoints
        "funcx_ep": conf['endpoint'],
        "funcx_local_ep": conf['local_endpoint'],
    }
}

phils_client = Kanzus_Phils_Client()
phils_flow = phils_client.run_flow(flow_input=flow_input)
