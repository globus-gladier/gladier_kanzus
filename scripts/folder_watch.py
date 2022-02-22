#!/local/data/idsbc/idstaff/gladier/miniconda3/envs/gladier/bin/python

import time, argparse, os
from watchdog.observers import Observer
#from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

class KanzusTriggers:
    def __init__(self, folder_path):
        self.observer = Observer()
        self.folder_path = folder_path

    def run(self):
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
        print(event)
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            KanzusLogic(event.src_path)
            return None
        elif event.event_type == 'modified':
            KanzusLogic(event.src_path)
            return None


def KanzusLogic(event_file):
    print(event_file)
    
# Arg Parsing
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('localdir', type=str, default='.')
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    local_dir = args.localdir

    os.chdir(local_dir)

    exp = KanzusTriggers(local_dir)
    exp.run()



