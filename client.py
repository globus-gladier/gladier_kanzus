from gladier import GladierBaseClient


class KanzusClient(GladierBaseClient):
    gladier_tools = [
    ]
    flow_definition = ##TODO change that to the original flow ryan was using
##

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

class KanzusTriggers:
    def __init__(self, folder_path):
        self.observer = Observer()
        self.folder_path = folder_path 

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Kanzus Triggers Stopped")
  
        self.observer.join()

class Handler:(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':

            #event.src_path is the file watchdog found
            # Event is created, you can process it now
            KanzusLogic(event.src_path,f_pattern=None,f_ext=None, n_batch=256)
  

def KanzusLogic(cbf_file,f_pattern=None,f_ext=None, n_batch=256):
        print(cbf_file)

        ##cbf is created
        ##n_batch runs plot
        ##cbf name  %n_batch==0
        ## 





##Arg Parsing
def parse_args():
    parser = argparse.ArgumentParser()
    ##
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    logger = logging.getLogger()
    if args.verbose:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)

    kanzus_cli = Kanzus_Client()
    kanzus_cli.get_input()

    # if args.dry_run:
    #     print(json.dumps(flow_input, indent=2))
    #     sys.exit()
    # else:
    #     corr_flow = corr_cli.run_flow(flow_input=flow_input)
    #     corr_cli.check_flow(corr_flow['action_id'])


    buckets = ['/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00256.cbf',
               '/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00512.cbf',
               '/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00768.cbf']
    res = create_flow_input(buckets)
    from pprint import pprint
    pprint(res)
