#!/local/data/idsbc/idstaff/gladier/miniconda3/envs/gladier/bin/python

from ssl import ALERT_DESCRIPTION_PROTOCOL_VERSION
import time, argparse, os
from watchdog.observers import Observer
#from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
import gladier_kanzus.logging  # noqa

class KanzusTriggers:
    def __init__(self, folder_path):
        self.observer = Observer()
        self.folder_path = folder_path

    def run(self):
        print("Kanzus Client Started")
        if not os.path.isdir(self.folder_path):
            print("  Monitor dir does not exist.")
            print("  Dir " + self.folder_path + " was created")
            os.mkdir(self.folder_path)
        

        os.chdir(self.folder_path)
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
#        print(event)
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            #KanzusLogic(event.src_path)
            return None
        elif event.event_type == 'modified':
            KanzusLogic(event.src_path)
            return None

def parse_event(event_file):
    #Creates payload based on file names
    #Could eventually be merged with the base_payload and simplify the flow submission
    event = {}
    event['exp'] = event_file.split('/')[-4]
    event['sample'] = event_file.split('/')[-3]
    event['chip_letter'] = event_file.split('/')[-2][0]
    event['filename'] = os.path.basename(event_file)
    event['chip_name'] = event['filename'].split('_')[0]
    event['run_num'] = int(event['filename'].split('_')[1])
    
    try:
        event['cbf_num'] = int(event['filename'].split('_')[2].replace('.cbf',''))
    except:
        event['cbf_num'] = -1

    try:
        with open(event_file) as f:
            intlist = [line for line in f]
        event['total_ints'] = len(intlist)
    except:
        event['total_ints'] = -1
    
    return event


def KanzusLogic(event_file):
    ##Parses each event and checks if it is a cbf file or int_list file
    ##Each event updates the global base_input that is used for triggering the flows.
    
    if event_file.endswith('.cbf') or event_file.endswith('_proc_ints.txt'):
        event = parse_event(event_file)
    else:
        event = None
        return


    # LOCAL processing dirs
    local_exp_path = base_input["input"]["base_local_dir"]
    base_input["input"]["local_data_dir"] = os.path.join(local_exp_path, event['sample'], event['chip_letter'])
    base_input["input"]["local_proc_dir"] = os.path.join(local_exp_path, event['sample'], event['chip_name']) + '_proc'
    base_input["input"]["local_prime_dir"] = os.path.join(local_exp_path, event['sample'], event['chip_name']) + '_prime'
    base_input["input"]["local_images_dir"] = os.path.join(local_exp_path, event['sample'], event['chip_name']) + '_images'

    # REMOTE processing dirs
    remote_exp_path = base_input["input"]["base_data_dir"]
    base_input["input"]["data_dir"] = os.path.join(remote_exp_path, event['sample'], event['chip_letter'])
    base_input["input"]["proc_dir"] = os.path.join(remote_exp_path, event['sample'], event['chip_name']) + '_proc'
    base_input["input"]["prime_dir"] = os.path.join(remote_exp_path, event['sample'], event['chip_name']) + '_prime'
    base_input["input"]["upload_dir"] = os.path.join(remote_exp_path, event['sample'], event['chip_name']) + '_images' 
    
    # Common Experiment variables
    base_input["input"]["trigger_name"] = event_file
    
    base_input["input"]['filename'] = event['filename']
    base_input["input"]['exp'] = event['exp']
    base_input["input"]['sample'] = event['sample']
    base_input["input"]['chip_letter'] = event['chip_letter']
    base_input["input"]['chip_name'] = event['chip_name']
    base_input["input"]['run_num'] = event['run_num']
    base_input["input"]['cbf_num'] = event['cbf_num']
    
    base_input["input"]['stills_batch_size'] = n_batch_stills
    
    base_input['input']['tar_input'] = base_input["input"]["proc_dir"] ##Something funky here 
    base_input['input']['tar_output'] = os.path.join(base_input["input"]["upload_dir"],'ints.tar.gz')
    base_input['input']['pilot'] = {}

    ##Basic trigger structure
    ## each line checks if some variable (cbf_num) extracted from the event name matches
    ## each flow have the exact same structure and receives the same payload created by the event_parser
    if event['cbf_num'] == 512:
        start_transfer_flow(event)

    if event['cbf_num'] % n_batch_transfer == 0:
        start_transfer_flow(event)

    if event['cbf_num'] % n_batch_stills == 0:
        start_stills_flow(event)

    if event['cbf_num'] % n_batch_publish == 0:
        start_publish_flow(event)
    
    #if event['cbf_num'] % n_batch_prime == 0:
    #    start_prime_flow(event)

    if event['total_ints'] > min_ints_prime:
        start_prime_flow(event)
    elif event['total_ints'] > 0:
        print('Not enough ints for prime: '+str(event['total_ints']))

    ###Standard structure to run a flow. 
    # It receives a parsed event
    # creates a label based on the event
    # run flow based on the created payload
    # prints the url for records.


    
def start_transfer_flow(event):
    label = 'SSX_Transfer_{}_{}'.format(event['chip_name'],event['cbf_num'])
    flow = data_transfer_flow.run_flow(flow_input=base_input,label=label)
    print(label)
    print("URL : https://app.globus.org/runs/" + flow['action_id'] + "\n")

def start_stills_flow(event):
    label = 'SSX_Stills_{}_{}'.format(event['chip_name'],event['cbf_num'])
    flow = stills_flow.run_flow(flow_input=base_input, label=label)
    print(label)
    print("URL : https://app.globus.org/runs/" + flow['action_id'] + "\n")


def start_publish_flow(event):
    label = 'SSX_Zip_{}_{}'.format(event['chip_name'],event['cbf_num'])
    flow = publish_flow.run_flow(flow_input=base_input,label=label)
    print(label)
    print("URL : https://app.globus.org/runs/" + flow['action_id'] + "\n")

def start_prime_flow(event):                                   
    label = 'SSX_Prime_{}_{}'.format(event['chip_name'],event['total_ints'])                                                                                                                                    
    flow = prime_flow.run_flow(flow_input=base_input, label=label)
    print(label)
    print("URL : https://app.globus.org/runs/" + flow['action_id'] + "\n")

# Arg Parsing
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('localdir', type=str, default='.')
    parser.add_argument('--datadir', type=str, 
        default='/eagle/APSDataAnalysis/SSX/random_start')
    parser.add_argument('--deployment','-d', default='raf-prod', help=f'Deployment configs. Available: {list(deployment_map.keys())}')
    return parser.parse_args()

##Gather deployment specific variables
from gladier_kanzus.deployments import deployment_map

##Import relevant flows
from gladier_kanzus.flows import TransferFlow
from gladier_kanzus.flows import StillsFlow
from gladier_kanzus.flows import PublishFlow
from gladier_kanzus.flows import PrimeFlow



if __name__ == '__main__':

    args = parse_args()

    # Experiment paths
    # localdir should match the beamline S# path where data will be acquired
    # data_dir sets where data will be transfered and processed at the computing resource 
    local_dir = args.localdir
    data_dir = args.datadir


    # Basic triggers for each flow based on the cbf_num of each file acquired
    # Current logic will trigger each flow at multiples of this variables 
    ##
    n_batch_transfer = 2048
    data_transfer_flow = TransferFlow()
    ##    
    n_batch_stills = 512
    stills_flow = StillsFlow()
    ##
    n_batch_publish =  2048
    publish_flow = PublishFlow()
    ##
    n_batch_prime =  2000
    min_ints_prime = 1000
    prime_flow = PrimeFlow()

    # Sets used deployment
    depl = deployment_map.get(args.deployment)
    if not depl:
        raise ValueError(f'Invalid Deployment, deployments available: {list(deployment_map.keys())}')

    depl_input = depl.get_input()

    # Base input for the flow
    base_input = {
        "input": {
            #Processing variables
            "base_local_dir": local_dir,
            "base_data_dir": data_dir,
            
            # globus local endpoint
            "globus_local_ep": depl_input['input']['beamline_globus_ep'],

            # globus endpoint and mount point for remote resource
            "globus_dest_ep": depl_input['input']['theta_globus_ep'], 
    	    "globus_dest_mount" : depl_input['input']['ssx_eagle_mount'],

            # funcX endpoints
            'funcx_endpoint_non_compute': depl_input['input']['funcx_endpoint_non_compute'],
            'funcx_endpoint_compute': depl_input['input']['funcx_endpoint_compute'],

            # Publication index and project
            ## maybe this should go to deployments.
            'search_index': '5e63bb08-5b39-4a02-86f3-44cec03e8bc0',
            'search_project': 'ssx',
            'source_globus_endpoint': '08925f04-569f-11e7-bef8-22000b9a448b',
            # Extra groups can be specified here. The SSX Admin group will always
            # be provided automatically.
            'groups': []
        }
    }

    ##Creates and starts the watcher
    exp = KanzusTriggers(local_dir)
    exp.run()



