import datetime
import logging
import re
import os

from ..gladier.kanzus.dials import funcx_create_phil, funcx_stills_process, funcx_plot_ssx, funcx_prime
from ..gladier.kanzus.pilot import funcx_pilot

import flow_definition

from globus_automate_client import (create_flows_client, graphviz_format, state_colors_for_log,
                                    get_access_token_for_scope, create_action_client,
                                    create_flows_client)

from configobj import ConfigObj

from funcx.sdk.client import FuncXClient

log = logging.getLogger(__name__)


class KanzusClient(object):
    """Main class for dealing with SSX functions and flows
    Providers helper operations to create and cache function and flow ids.
    """

    CONF_FILE = os.path.expanduser('~') + "/.kanzus.cfg"
    CLIENT_ID = "e6c75d97-532a-4c88-b031-8584a319fa3e"

    def __init__(self, force_login=False, **kwargs):

        self.fxc = FuncXClient(no_local_server=kwargs.get("no_local_server", True),
                               no_browser=kwargs.get("no_browser", True),
                               refresh_tokens=kwargs.get("refresh_tokens", True),
                               force=force_login)

        # Load functions and flow ids if they exist
        config = ConfigObj(self.CONF_FILE, create_empty=True)
        try:
            self.fxid_phil = config['funcx_phil']
            self.fxid_stills = config['funcx_stills']
            self.fxid_plot = config['funcx_plot']
            self.fxid_pilot = config['funcx_pilot']
            self.fxid_prime = config['funcx_prime']
        except KeyError as e:
            # Create if they don't exist
            self.register_functions()

        try:
            self.auto_flowid = config['automate_flowid']
            self.auto_scope = config['automate_scope']
        except KeyError as e:
            # Create if they don't exist
            self.register_flow()

    def start_flow(self, flow_input):
        """
        Initiate the flow.
        """

        flows_client = create_flows_client(self.CLIENT_ID)

        flow_action = flows_client.run_flow(self.auto_flowid, self.auto_scope, flow_input)
        flow_action_id = flow_action['action_id']
        flow_status = flow_action['status']

        return flow_action_id

    def register_functions(self):
        """Register the functions with funcx and store their ids
        Returns
        -------
        dict: phil, stills, plot
        """

        self.fxid_phil = self.fxc.register_function(funcx_create_phil,
                                                    description="Create the phil file for analysis.")
        self.fxid_stills = self.fxc.register_function(funcx_stills_process,
                                                      description="Process stills images.")
        self.fxid_plot = self.fxc.register_function(funcx_plot_ssx,
                                                    description="Plot stills images.")
        self.fxid_pilot = self.fxc.register_function(funcx_pilot,
                                                     description="Upload with pilot.")
        self.fxid_prime = self.fxc.register_function(funcx_prime,
                                                     description="Upload with pilot.")

        # Save them to the config
        config = ConfigObj(self.CONF_FILE, create_empty=True)
        config['funcx_phil'] = self.fxid_phil
        config['funcx_stills'] = self.fxid_stills
        config['funcx_plot'] = self.fxid_plot
        config['funcx_pilot'] = self.fxid_pilot
        config['funcx_prime'] = self.fxid_prime
        config.write()

        return {'phil': self.fxid_phil, 'stills': self.fxid_stills,
                'plot': self.fxid_plot, 'pilot': self.fxid_pilot, 'prime': self.fxid_prime}

    def register_flow(self):
        """Register the automate flow and store its id and scope
        Returns
        -------
        dict : id and scope
        """
        flows_client = create_flows_client(self.CLIENT_ID)

        flow = flows_client.deploy_flow(flow_definition, title="SSX Flow")
        self.auto_flowid = flow['id']
        self.auto_scope = flow['globus_auth_scope']

        config = ConfigObj(self.CONF_FILE, create_empty=True)
        config['automate_flowid'] = self.auto_flowid
        config['automate_scope'] = self.auto_scope
        config.write()

        return {'id': self.auto_flowid, 'scope': self.auto_scope}

    def parse_pathnames(self, pathnames):
        # assert len(pathnames) > 0, f'Must have at least one pathname to generate inputs!!'
        # # This *should* find the largest file given, such as 'Akaroa5_6_00709.cbf'
        # file_number = int(pathnames.split("_")[-1].replace(".cbf", ""))
        # range_step = 256
        # if highest_cbf <= range_step:
        #     return [f'00001..{str(highest_cbf).zfill(5)}']
        #
        # total_range = range(1, highest_cbf, range_step)
        #
        # # for 760, would create 1..256, 257..512, 513..768
        # numeric_ranges = [[i, i + range_step - 1] for i in total_range]
        # # Fix the final range, which will be off by range_step - highest_cbf
        # # simply set it to the highest cbf
        # numeric_ranges[-1][1] = highest_cbf
        #
        #
        # return [f'{str(low).zfill(5)}..{str(high).zfill(5)}'
        #         for low, high in numeric_ranges]
        chip_name = exp_num = None
        # start at 1
        ranges = []
        for pathname in pathnames:
            print(pathname)
            match = re.match(
                r'(?P<exp_name>[\d\w]+)_(?P<exp_num>\d+)_(?P<max_cbf>\d+).cbf',
                os.path.basename(pathname),
            )
            assert match, 'Pathname must match name_exp_max_cbf, such as "Akaroa5_6_00709.cbf"!' + pathname
            einfo = match.groupdict()
            chip_name, exp_num = einfo['exp_name'], einfo['exp_num']
            max_cbf_num = int(einfo['max_cbf'])
            if not ranges:
                start = max_cbf_num - 256
                if start == 0:
                    ranges = [1]
                else:
                    ranges = [start]
            ranges.append(int(einfo['max_cbf']))
        log.debug(f'Raw ranges are {ranges}')

        # creates a list of numeric ranges: [[1, 256], [257, 512]]
        numeric_ranges = []
        for index in range(len(ranges) - 1):
            low = ranges[index] + 1
            high = ranges[index + 1]
            numeric_ranges.append([low, high])
        # We offset each range by one so they don't overlap, but that means
        # the very first range will be off by one. Fix the very first range
        numeric_ranges[0][0] -= 1

        zfilled_ranges = [str(f'{str(low).zfill(5)}..{str(high).zfill(5)}')
                          for low, high in numeric_ranges]
        return {
            'ranges': zfilled_ranges,
            'exp_num': exp_num,
            'exp_name': chip_name
        }

    def create_funcx_payload(self, pathnames, run_name="S8", nproc=256,
                             beamx='-214.400', beamy='218.200',
                             aps_data_root="/gdata/dm/SBC/ssx8/monday-go-7/",
                             theta_root='/projects/APSDataAnalysis/SSX/',
                             pilot=None, mask_file="mask.pickle", unit_cell=None, dmin="2.1"):
        """Create the automate flow_input document.
        Parameters
        ----------
        pathnames : [str]
            The list of the filenames triggering analysis (multiples of 256)
        run_name : str
            The name of the SSX run (S8, S9)
        nproc : int
            The number of processes to use in the phil file
        beamx : str
            The beamx coord
        beamy : str
            The beamy coord
        aps_data_root : str
            The root directory on aps#data
        theta_root : str
            The root directory to transfer files to on alcf#dtn_theta
        funcx_login : str
            The login EP to use on Theta
        funcx_theta : str
            The theta queue EP to use
        mask_file : str
            The mask path to be added to the Phil file
        unit_cell : str
            A comma separated list of numbers
        dmin : str
            The dmin to use in PRIME
        Returns
        -------
        json : the flow input
        """
        if not theta_root.endswith('/'):
            theta_root += '/'
        base_path = pathnames[0]
        info = self.parse_pathnames(pathnames)
        source_path = f'/net/data/idsbc/idstaff/{run_name}/'
        theta_path = f'{theta_root}{run_name}/'
        aps_source = base_path.replace(source_path, aps_data_root)
        theta_dest = base_path.replace(source_path, theta_path)
        theta_base = os.path.dirname(theta_dest)

        log.debug(f'Source Path: {source_path}')
        log.debug(f'Theta Path: {theta_path}')
        log.debug(f'aps_source Path: {aps_source}')
        log.debug(f'Theta_dest Path: {theta_dest}')

        # Metadata is delivered directly to pilot to be uploaded to the portal
        # Anything here will be discoverable by Globus Search
        metadata = {
            "description": f"Automated data processing.",
            "creators": [{"creatorName": "Kanzus"}],
            "publisher": "Automate",
            "title": f'SSX {info["exp_name"].capitalize()} Chip',
            "subjects": [{"subject": "SSX"}],
            "publicationYear": str(datetime.datetime.now().year),
            "resourceType": {
                "resourceType": "Dataset",
                "resourceTypeGeneral": "Dataset"
            },
            "batch_info": {},
            "chip": info['exp_name'].capitalize(),
            "experiment_number": info['exp_num'],
            "run_name": run_name,
            "aps_data": aps_data_root,
            "trigger_name": pathnames[-1]
        }

        exp_input = os.path.join(
            theta_base,
            f'{info["exp_name"]}_{info["exp_num"]}_'
        )
        stills_payload = [{
           'input_files': f"{exp_input}" + "{" + r + "}.cbf",
           'beamx': beamx,
           'beamy': beamy,
           'nproc': nproc,
           'unit_cell': unit_cell,
           'mask': mask_file,
           'input_range': r,
           'phil_file': f'{theta_base}/process_{info["exp_num"]}.phil',
           'metadata': metadata,
           'dmin': dmin,
           'pilot': pilot or {}
        } for r in info['ranges']]
        general_payload = stills_payload[-1]
        return {
            'transfer': {
                "source_endpoint_id": "9c9cb97e-de86-11e6-9d15-22000a1e3b52",
                "destination_endpoint_id": "08925f04-569f-11e7-bef8-22000b9a448b",
                "sync_level": "exists",
                "transfer_items": [{
                    "source_path": os.path.dirname(aps_source),
                    "destination_path": os.path.dirname(theta_dest),
                    "recursive": True
                }]
            },
            'funcx_phil': general_payload,
            'funcx_stills': stills_payload,
            'funcx_plot': general_payload,
            'funcx_prime': general_payload,
            'funcx_pilot': general_payload,
        }


    def create_flow_tasks(self, payload, funcx_worker, funcx_login=None):
        """
        'funcx_phil': payload,
        'funcx_stills': stills_payload,
        'funcx_plot': payload,
        'funcx_pilot': payload,
        'funcx_prime': payload,
        """
        if funcx_login is None:
            funcx_login = funcx_worker
        return {
            "Transfer1Input": payload['transfer'],
            "Exec1Input": {
                "tasks": [{
                    "endpoint": funcx_worker,
                    "func": self.fxid_phil,
                    "payload": payload['funcx_phil']
                }]
            },
            "Exec2Input": {
                "tasks": [{
                    "endpoint": funcx_worker,
                    "func": self.fxid_stills,
                    "payload": p
                } for p in payload['funcx_stills']]
            },
            "Exec3Input": {
                "tasks": [{
                    "endpoint": funcx_worker,
                    "func": self.fxid_plot,
                    "payload": payload['funcx_plot']
                }]
            },
            "Exec4Input": {
                "tasks": [{
                    "endpoint": funcx_worker,
                    "func": self.fxid_prime,
                    "payload": payload['funcx_prime']
                }]
            },
            "Exec5Input": {
                "tasks": [{
                    "endpoint": funcx_login,
                    "func": self.fxid_pilot,
                    "payload": payload['funcx_pilot']
                }]
            }
        }

    def create_flow_input(self, pathnames, run_name="S8", nproc=256,
                          beamx='-214.400', beamy='218.200', aps_data_root="/gdata/dm/SBC/ssx8/monday-go-7/",
                          funcx_login="6c4323f4-a062-4551-a883-146a352a43f5",
                          funcx_theta="670b42d1-7df8-423e-b651-292979a861a5",
                          pilot=None, mask_file="mask.pickle", unit_cell=None, dmin="2.1"):
        """
        Parameters
        ----------
        pathname : str
            The name of the file being acted upon
        batch_size : int
            The number of files being processed
        task_size : int
            The number of files to process each task
        run_name : str
            The name of the SSX run (S8, S9)
        nproc : int
            The number of processes to use in the phil file
        beamx : str
            The beamx coord
        beamy : str
            The beamy coord
        aps_data_root : str
            The root directory on aps#data
        funcx_login : str
            The login EP to use on Theta
        funcx_theta : str
            The theta queue EP to use
        dmin : str
            The dmin to use in PRIME
        pilot : dict
            Optional args for publishing to search
            {
                'config': '~/.pilot-kanzus.cfg',
                'context': 'kanzus',
                'project': 'ssx-test',
                'local_endpoint': '08925f04-569f-11e7-bef8-22000b9a448b',
                'dry_run': True,
            }
        Returns
        -------
        json : the flow input
        Create the automate flow_input document.
        # Now create tasks for every bucket we are processing
        for pathname in pathnames:
            file_number = int(pathname.split("_")[-1].replace(".cbf", ""))
            start_range = str(file_number - 255).zfill(5)
            end_range = str(file_number).zfill(5)
            input_range = f"{start_range}..{end_range}"
            raw_files = "_".join(pathname.split("_")[:-1]) + "_{" + input_range + "}.cbf"
            input_files = raw_files.replace(source_path, theta_path)
            payload = {'input_files': input_files,
                       'beamx': beamx,
                       'beamy': beamy,
                       'nproc': nproc,
                       'input_range': input_range,
                       'phil_file': f'{work_path}/process_{exp_num}.phil',
                       'metadata': metadata,
                       'dmin': dmin}
            task_dict = {"endpoint": funcx_theta,
                         "func": self.fxid_stills,
                         "payload": payload}
        """

        payload = self.create_funcx_payload(
            pathnames,
            run_name=run_name,
            nproc=nproc,
            beamx=beamx,
            beamy=beamy,
            aps_data_root=aps_data_root,
            pilot=pilot,
            mask_file=mask_file,
            unit_cell=unit_cell,
            dmin=dmin
        )
        return self.create_flow_tasks(payload, funcx_theta, funcx_login=funcx_login)


if __name__ == '__main__':
    kc = KanzusClient()
    buckets = ['/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00256.cbf',
               '/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00512.cbf',
               '/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00768.cbf']
    res = kc.create_flow_input(buckets)
    from pprint import pprint
    pprint(res)