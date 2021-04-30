def funcx_pilot(data):
    """
    Data should be a dict containing the following.
    * input_files -- A range-path filename which should expand in bash to
      all of the files that should be collected. For example:
    /projects/APSDataAnalysis/SSX/S8/nsp10nsp16/A/Akaroa5_6_{00001..00256}.cbf
    * metadata -- Metadata dict to be uploaded to search. See pilot docs for
      details:
    https://github.com/globusonline/pilot1-tools/blob/master/docs/reference.rst#metadata  # noqa
    * pilot -- dict of extra pilot args, Ex:
        {
            'config': '~/.pilot-kanzus.cfg',
            'context': 'kanzus',
            'project': 'ssx-test',
            'local_endpoint': '08925f04-569f-11e7-bef8-22000b9a448b',
            'dry_run': False,  # Don't upload result, just do test run
        }
    """
    import os
    import json
    import pilot.client

    exp_name = data['metadata']['chip']
    exp_num = data['metadata']['experiment_number']
    run_dir = os.path.dirname(data['input_files'])
    # Ex: /projects/APSDataAnalysis/SSX/S8/nsp10nsp16/A/Akaroa5_processing
    proc_dir = os.path.join(run_dir, f'{exp_name}_processing')
    assert os.path.exists(run_dir), f'"input_files" dir does not exist: {run_dir}'
    assert os.path.exists(proc_dir), f'processing dir does not exist: {proc_dir}'

    # Ex: /projects/APSDataAnalysis/SSX/S8/nsp10nsp16/A/Akaroa5_images
    image_dir = os.path.join(run_dir, f'{exp_name}_images')
    # Ex: /projects/APSDataAnalysis/SSX/S8/nsp10nsp16/A/beamline_run6.json
    beamline_file = os.path.join(run_dir, f'beamline_run{exp_num}.json')

    os.chdir(proc_dir)
    dir_contents = os.listdir()

    cbf_files = []
    int_files = []
    for filename in dir_contents:
        if 'int-' in filename:
            int_files.append(filename)
        elif 'datablock.json' in filename:
            cbf_files.append(filename)

    min_cbf = 1000000
    max_cbf = 0
    for filename in cbf_files:
        tmp_name = int(filename.split("_")[-2])
        if tmp_name > max_cbf:
            max_cbf = tmp_name
        elif tmp_name < min_cbf:
            min_cbf = tmp_name

    metadata = data['metadata']

    metadata['batch_info']['cbf_files'] = len(cbf_files)
    metadata['batch_info']['cbf_file_range'] = {'from': min_cbf, 'to': max_cbf}
    metadata['batch_info']['total_number_of_int_files'] = len(int_files)

    # Read in the beamline.json file
    with open(beamline_file, 'r') as fp:
        beamline_meta = json.load(fp)
    try:
        metadata.update(beamline_meta)
        metadata['protein'] = beamline_meta['user_input']['prot_name']
    except:
        pass

    pargs = data.get('pilot', {})
    pc = pilot.client.PilotClient()
    assert pc.is_logged_in(), 'Please run `pilot login --no-local-server`'
    assert pc.context.current == pargs.get('context', 'kanzus'), 'Please run `pilot context set kanzus`'
    pc.project.current = pargs.get('project', 'ssx')
    # Set this to the local Globus Endpoint
    local_endpoint = pargs.get('local_endpoint', '08925f04-569f-11e7-bef8-22000b9a448b')
    pc.profile.save_option('local_endpoint', local_endpoint)
    assert image_dir.endswith('_images'), f'Filename {image_dir} DOES NOT appear to be correct'
    result = pc.upload(image_dir, '/', metadata=data['metadata'], update=True, skip_analysis=True,
                     dry_run=pargs.get('dry_run', False))
    # For some reason, these cause problems. Delete them before returning.
    del result['previous_metadata']
    del result['upload']

    return result