#!/local/data/idsbc/idstaff/gladier/miniconda3/envs/gladier/bin/python
import pathlib
import time, argparse, os, re
from pprint import pprint
import numpy as np
#from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from gladier import GladierBaseClient, generate_flow_definition

class KanzusTriggers:
    def __init__(self, folder_path):
        self.observer = Observer()
        self.folder_path = folder_path

    def run(self,pattern=None):
        print("Kanzus Triggers Started")
        if not os.path.isdir(self.folder_path):
            print("Monitor dir does not exist.")
            print("Dir " + self.folder_path + " was created")
            os.mkdir(self.folder_path)
            
        print("Monitoring: " + self.folder_path)
        print('')

        event_handler = Handler()
        self.observer.schedule(event_handler, self.folder_path, recursive = True)
        
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Kanzus Triggers Stopped")

        self.observer.join()

#https://stackoverflow.com/questions/58484940/process-multiple-oncreated-events-parallelly-in-python-watchdog
class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        #print(event)
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            KanzusLogic(event.src_path)
            return None
        elif event.event_type == 'modified':
            KanzusLogic(event.src_path)
            return None


def KanzusLogic(event_file):
    #cbf_num_pattern = r'(\w+_\d+_)(\d+).cbf' ##old pattern
    cbf_num_pattern = r'(\w+)\/(\w+)\/(\w+)\/(\w+)_(\d+)_(\d+).cbf'
    cbf_parse = re.match(cbf_num_pattern, event_file)
#    print(cbf_parse)
#    print(event_file)

#    if cbf_parse is not None:
    if '.cbf' in event_file:
        exp_path = base_input["input"]["base_local_dir"]
        #exp = cbf_parse.group(1)
        #sample = cbf_parse.group(2)
        #chip_letter = cbf_parse.group(3)
        #chip_name = cbf_parse.group(4)
        #run_num = int(cbf_parse.group(5)) 
        #cbf_num = int(cbf_parse.group(6))
        exp = event_file.split('/')[-4]
        sample = event_file.split('/')[-3]
        chip_letter = event_file.split('/')[-2]
        filename = event_file.split('/')[-1]
        chip_name = filename.split('_')[0]
        run_num = int(filename.split('_')[1])
        try:
            cbf_num = int(filename.split('_')[2].replace(".cbf",""))
        except:
            return
        #print(cbf_num)
        # LOCAL processing dirs
        local_dir = os.path.join(exp_path, sample, chip_letter)
        base_input["input"]["local_dir"] = local_dir
        base_input["input"]["local_proc_dir"] = local_dir + '_proc'
        base_input["input"]["local_upload_dir"] = os.path.join(exp_path, sample, chip_name) + '_images'

        # REMOTE processing dirs
        data_dir = os.path.join(base_input["input"]["base_data_dir"], sample, chip_letter)
        base_input["input"]["data_dir"] = data_dir
        base_input["input"]["proc_dir"] = data_dir + '_proc'
        base_input["input"]["upload_dir"] = os.path.join(base_input["input"]["base_data_dir"], sample, chip_name) + '_images' 
        base_input["input"]["trigger_name"] = event_file

        if cbf_num % n_batch_transfer == 0 or cbf_num == n_initial_transfer:
            start_transfer_flow(event_file, sample, chip_letter, cbf_num)

        if cbf_num % n_batch_stills == 0:
            start_stills_flow(event_file, sample, chip_letter, chip_name, run_num, cbf_num)

        if cbf_num % n_batch_plot == 0:
            start_plot_flow(event_file, sample, chip_letter, chip_name, cbf_num)

        # if cbf_num%n_batch_prime==0:                                                                        
            # start_prime_flow(event_file, cbf_num)   


    #cbf_num_pattern = r'(\w+_\d+_)(\d+).cbf' ##old pattern
    # proc_pattern = r'(\w+)\/(\w+)\/(\w_proc)\/(\w+)_(\d+)_(\d+).cbf'
    # cbf_parse = re.match(cbf_num_pattern, event_file)

def start_prime_flow(event_file, cbf_num, cbf_base):
    subranges = create_ranges(cbf_num-n_batch_stills, cbf_num, n_batch_stills)                      
    new_range = subranges[0]                                                                        
    base_input["input"]["input_files"]=f"{cbf_base}{new_range}.cbf"                                 
    base_input["input"]["input_range"]=new_range[1:-1]                                              
                                                                                                            
    label = f'SSX_Prime_{names[0]}_{new_range}'                                                    
                                                                                                            
    flow = prime_client.run_flow(flow_input=base_input, label=label)                               
                                                                                                            
    print('Prime Flow')                                                                            
    print("  Local Trigger : " + event_file)                                                        
    print("  Range : " + base_input["input"]["input_range"])                                        
    print("  UUID : " + flow['action_id'])
    print("  URL : https://app.globus.org/runs/" + flow['action_id'] + "\n")


def start_stills_flow(event_file, sample, chip_letter, chip_name, run_num, cbf_num):
    subranges = create_ranges(cbf_num - n_batch_stills, cbf_num, n_batch_stills)
    new_range = subranges[0]
    label = f'SSX_Stills_{sample}_{chip_letter}_{new_range}'

    flow_input = base_input.copy()
    flow_input["input"]["input_files"]=f"{chip_name}_{run_num}_{new_range}.cbf"
    flow_input["input"]["input_range"]=new_range[1:-1]

    flow = stills_flow.run_flow(flow_input=flow_input, label=label)

    print('Stills Flow')
    print("  Local Trigger : " + event_file)
    print("  Range : " + base_input["input"]["input_range"])
    print("  UUID : " + flow['action_id'])
    print("  URL : https://app.globus.org/runs/" + flow['action_id'] + "\n")

def start_transfer_flow(event_file, sample, chip_letter, cbf_num):
    label = f'SSX_Transfer_{sample}_{chip_letter}_{cbf_num}'
    flow = data_transfer_flow.run_flow(flow_input=base_input,label=label)

    print('Transfer Flow')
    print("  Local Trigger : " + event_file)
    print("  UUID : " + flow['action_id'])
    print("  URL : https://app.globus.org/runs/" + flow['action_id'] + "\n")

def start_plot_flow(event_file, sample, chip_letter, chip_name, cbf_num):
    label = f'SSX_Plot_{sample}_{chip_letter}_{cbf_num}'
    flow_input = base_input.copy()

    flow_input['input']['tar_input'] = str(pathlib.Path(flow_input["input"]["upload_dir"]).parent / 'ints')
    flow_input['input']['tar_output'] = str(pathlib.Path(flow_input["input"]["upload_dir"]) / 'ints.tar.gz')

    flow_input['input']['pilot'] = {
        # This is the directory which will be published to petrel
        'dataset': flow_input['input']['upload_dir'],
        'index': '5e63bb08-5b39-4a02-86f3-44cec03e8bc0',
        'project': 'ssx',
        'source_globus_endpoint': '08925f04-569f-11e7-bef8-22000b9a448b',
        # Extra groups can be specified here. The SSX Admin group will always
        # be provided automatically.
        'groups': [],
    }

    flow = plot_flow.run_flow(flow_input=base_input,label=label)

    print('Plot and Publish Flow')
    print("  Local Trigger : " + event_file)
    print("  UUID : " + flow['action_id'])
    print("  URL : https://app.globus.org/runs/" + flow['action_id'] + "\n")
 


@generate_flow_definition
class TransferFlow(GladierBaseClient):
    gladier_tools = [
        'gladier_kanzus.tools.TransferOut',
    ]


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


@generate_flow_definition(modifiers={
    'tar': {'endpoint': 'funcx_endpoint_non_compute'},
    'ssx_plot': {'payload': '$.SsxGatherData.details.result[0].plot'},
    'publish_gather_metadata': {'WaitTime': 120, 'payload': '$.SsxGatherData.details.result[0].pilot'},
})
class PlotAndPublish(GladierBaseClient):
    gladier_tools = [
        'gladier_kanzus.tools.gather_data.SSXGatherData',
        'gladier_tools.posix.tar.Tar',
        'gladier_kanzus.tools.plot.SSXPlot',
        'gladier_tools.publish.Publish',
    ]


#@generate_flow_definition
#class PrimeFlow(GladierBaseClient):
#    gladier_tools = [
#        'gladier_kanzus.tools.Prime',
#        'gladier_kanzus.tools.TransferPrime',
#    ]

def create_ranges(start,end,delta):

    s_vec = np.arange(start,end,delta)
    proc_range = []
    for k in s_vec:
        k_start = k+1
        k_end = k_start + delta - 1
        if k_end > end:
            k_end = end
        proc_range.append(f'{{{str(k_start).zfill(5)}..{str(k_end).zfill(5)}}}')
    return proc_range

def register_container():
    from funcx.sdk.client import FuncXClient
    from gladier_kanzus.tools.dials_stills import stills_process

    fxc = FuncXClient()
    
    print('registering container')
    cont_dir =  '/eagle/APSDataAnalysis/SSX/containers/'
    container_name = "dials_v1.simg"

    cont_id = fxc.register_container(location=cont_dir+container_name,container_type='singularity')
    print('container id ', cont_id)
    
    return fxc.register_function(stills_process, container_uuid=cont_id)
    

# Arg Parsing
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('localdir', type=str, default='.')
    parser.add_argument('--datadir', type=str, 
        default='/APSDataAnalysis/SSX/random_start')
    return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()

    local_dir = args.localdir
    data_dir = args.datadir
    
    # triggers for data transfer BEAMLINE >> THETA
    n_initial_transfer = 128
    n_batch_transfer = 2048
    n_batch_transfer = 4096
    # triggers for stills batch procces (THETA)
    n_batch_stills = 256
    # triggers for prime batch procces (THETA)
    n_batch_plot =  1024
    # triggers for prime batch procces (THETA)
    n_batch_prime =  10000


    ##Process endpoints (theta - raf)
    funcx_endpoint_non_compute = 'e449e8b8-e114-4659-99af-a7de06feb847'
    funcx_endpoint_compute     = '4c676cea-8382-4d5d-bc63-d6342bdb00ca'

    ##Process endpoints (theta - Ryan)
    #funcx_endpoint_non_compute = '6c4323f4-a062-4551-a883-146a352a43f5'
    #funcx_endpoint_compute     = '9f84f41e-dfb6-4633-97be-b46901e9384c'   

    ##Transfer endpoints
    beamline_globus_ep = 'c7e7f102-2166-11ec-8338-9d23a2dd9550'
    eagle_globus_ep    = '05d2c76a-e867-4f67-aa57-76edeb0beda0'
    ssx_eagle_globus_ep ='4340775f-4758-4fd6-a7b1-990f82aef5de'
    theta_globus_ep    = '08925f04-569f-11e7-bef8-22000b9a448b'

    base_input = {
        "input": {
            #Processing variables
            "base_local_dir": local_dir,
            "base_data_dir": data_dir,

            "nproc": 32,
            "beamx": "-214.400",
            "beamy": "218.200",

            # funcX endpoints
            "funcx_endpoint_non_compute": funcx_endpoint_non_compute,
            "funcx_endpoint_compute": funcx_endpoint_compute,

            # globus endpoints
            "globus_local_ep": beamline_globus_ep,
            # "globus_dest_ep": eagle_globus_ep, 
	        "globus_dest_ep": theta_globus_ep,

            # container hack for stills
            "stills_process_funcx_id": register_container(),
        }
    }

    data_transfer_flow = TransferFlow()
    stills_flow = StillsFlow()
    plot_flow = PlotAndPublish()
    # prime_flow = PrimeFlow()

    os.chdir(local_dir)

    exp = KanzusTriggers(local_dir)
    exp.run()



