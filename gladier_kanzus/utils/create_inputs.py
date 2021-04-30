
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

