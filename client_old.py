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

   


if __name__ == '__main__':
    kc = KanzusClient()
    buckets = ['/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00256.cbf',
               '/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00512.cbf',
               '/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00768.cbf']
    res = kc.create_flow_input(buckets)
    from pprint import pprint
    pprint(res)