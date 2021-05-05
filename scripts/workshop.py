import time, argparse, os, re
from pprint import pprint
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gladier.client import GladierClient as GladierBaseClient

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

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            #event.src_path is the file watchdog found
            # Event is created, you can process it now
            KanzusLogic(event.src_path,f_pattern=None,f_ext=None, n_batch=256)


def KanzusLogic(event_file,f_pattern=None,f_ext=None, n_batch=256):
    if not f_pattern:
        f_pattern = r'(\w+_\d+_)(\d+).cbf'

    cbf_file = os.path.basename(event_file)
    cbf_parse = re.match(f_pattern, cbf_file)
    if cbf_parse is not None:
        cbf_base =cbf_parse.group(1)
        cbf_num =int(cbf_parse.group(2))

        n_batch_transfer = 256
        n_batch_plot = 1024
        
        range_delta = n_batch_transfer

        if cbf_num%n_batch_transfer==0:
            subranges = create_ranges(cbf_num-n_batch_transfer, cbf_num, range_delta)
            new_range = subranges[0]
            print('Transfer Flow')
            base_input["input"]["input_files"]=f"{cbf_base}{new_range}.cbf"
            base_input["input"]["input_range"]=new_range[1:-1]
            base_input["input"]["trigger_name"]= os.path.join(
                base_input["input"]["data_dir"], cbf_file
            )
            flow_input = base_input
            print("  Range : " + base_input["input"]["input_range"])
            #print(flow_input)
            workshop_flow = kanzus_workshop_client.start_flow(flow_input=flow_input)
            print("  UUID : " + workshop_flow['action_id'])
            print('')

        if cbf_num%n_batch_plot==0:
            print('Plot Flow')
            print("  UUID : " + workshop_flow['action_id'])
            print('')

from gladier_kanzus.flows.tutorial_flow import flow_definition as kanzus_flow
class KanzusSSXGladier(GladierBaseClient):
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
    gladier_tools = [
        'gladier_kanzus.tools.CreatePhil',
        'gladier_kanzus.tools.DialsStills',
        'gladier_kanzus.tools.SSXGatherData',
        'gladier_kanzus.tools.SSXPlot',
        'gladier_kanzus.tools.SSXPublish',
    ]
    flow_definition = kanzus_flow

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
    ##hacking over container
    from funcx.sdk.client import FuncXClient
    fxc = FuncXClient()
    from gladier_kanzus.tools.dials_stills import funcx_stills_process as stills_cont
    cont_dir =  '/home/rvescovi/.funcx/containers/'
    container_name = "dials_v1.simg"
    dials_cont_id = fxc.register_container(location=cont_dir+'/'+container_name,container_type='singularity')
    stills_cont_fxid = fxc.register_function(stills_cont, container_uuid=dials_cont_id)
    return stills_cont_fxid
    ##

##Arg Parsing
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('workdir', type=str, default='.')
    return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()

    workdir = args.workdir
    ##theta
    conf = {'local_endpoint': '8f2f2eab-90d2-45ba-a771-b96e6d530cad',
            'queue_endpoint': '23519765-ef2e-4df2-b125-e99de9154611',
            }

    ##theta dirs
    data_dir = '/eagle/APSDataAnalysis/SSX/workshop/O_test'
    proc_dir = data_dir + '_proc'
    upload_dir = data_dir + '_upl' 
    ##globus
    beamline_ep='87c4f45e-9c8b-11eb-8a8c-d70d98a40c8d'
    theta_ep='08925f04-569f-11e7-bef8-22000b9a448b'
    

    stills_cont_fxid = register_container()

    base_input = {
        "input": {
            #Processing variables
            "local_dir": workdir,
            "data_dir": data_dir,
            "proc_dir": proc_dir,
            "upload_dir": upload_dir,

            "nproc": 16,
            "beamx": "-214.400",
            "beamy": "218.200",

            # funcX endpoints
            "funcx_local_ep": conf['local_endpoint'],
            "funcx_queue_ep": conf['queue_endpoint'],

            # globus endpoints
            "globus_local_ep": beamline_ep,
            "globus_dest_ep": theta_ep, 

            # container hack for stills
            "stills_cont_fxid": stills_cont_fxid
        }
    }

    kanzus_workshop_client = KanzusSSXGladier()

    exp = KanzusTriggers(workdir)
    exp.run()



