from gladier import GladierBaseTool, generate_flow_definition
def ssx_gather_data(**data):
    import re
    import os
    import json
    import shutil
    import glob

    trigger_name = data['trigger_name']
    data_dir = data['data_dir']
    proc_dir = data['proc_dir']
    upload_dir = data['upload_dir']

    ##experiment information
    run_name = data['exp']
    protein= data['sample']
    chip_name = data['chip_name']
    run_num = data['run_num']

    beamline_file_name = f'beamline_run{run_num}.json'
    beamline_file = os.path.join(data_dir, beamline_file_name)

    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)
    
    if not os.path.isfile(os.path.join(upload_dir, beamline_file_name)):
        shutil.copy( beamline_file, upload_dir)

    int_indices = []
    int_filenames = []
    cbf_indices = []

    for int_file in glob.glob(os.path.join(proc_dir,'int-*.pickle')):
        int_file = os.path.basename(int_file)
        int_match = re.match(r'int-\d+-\w+_\d+_(\d+).pickle', int_file)
        if int_match:
            int_index = int_match.groups()[0]
            int_filenames.append(int_file)
            int_indices.append(int(int_index))

    for log_file in glob.glob(os.path.join(proc_dir,'log*.txt')):
        with open(log_file,'r') as f:
            for line in f.readlines():
                match = re.findall(r"\w+_\d+_(\d+).cbf", line)
                if match:
                    cbf_index = int(match[0])
                    cbf_indices.append(cbf_index)
    
    if len(cbf_indices) == 0:
        cbf_indices.append(0)
   
    proc_cbf_file = os.path.join(proc_dir,'proc_cbf.txt')
    
    if os.path.exists(proc_cbf_file):
        os.remove(proc_cbf_file)

    with open(proc_cbf_file,'w+') as f:
        for cbf in sorted(cbf_indices):
            f.write(str(cbf) + "\n")

    proc_ints_file = os.path.join(proc_dir,'proc_ints.txt')
    
    if os.path.exists(proc_ints_file):
        os.remove(proc_ints_file)

    with open(proc_ints_file,'w+') as f:
        for intfile in sorted(int_filenames):
            f.write(str(intfile) + "\n")
    
    batch_info = {
        'cbf_files': len(cbf_indices),
        'cbf_file_range': {'from': min(cbf_indices), 'to': max(cbf_indices)},
        'total_number_of_int_files': len(int_indices)
    }

    # Fetch beamline metadata
    with open(beamline_file, 'r') as fp:
        beamline_metadata = json.load(fp)

    user_input = beamline_metadata.get('user_input', {})
    protein = user_input.get('protein_name', protein)

    metadata = {
        # This is the directory which will be published
        'dataset': data['upload_dir'],
        'index': '5e63bb08-5b39-4a02-86f3-44cec03e8bc0',
        'project': 'ssx',
        'source_globus_endpoint': '08925f04-569f-11e7-bef8-22000b9a448b',
        # Extra groups can be specified here. The SSX Admin group will always
        # be provided automatically.
        'groups': [],    }

    # Update any metadata in the pilot 'metadata' key
    metadata = data['pilot'].get('metadata', {})
    metadata.update(beamline_metadata)
    metadata.update({
        'chip': chip_name,
        'experiment_number': run_num,
        'run_name': run_name,
        'protein': protein,
        'trigger_name': trigger_name,
        'batch_info': batch_info,
    })
    data['pilot']['metadata'] = metadata

    return {
        'pilot': data['pilot']
    }


@generate_flow_definition(modifiers={
    'ssx_gather_data': {'endpoint': 'funcx_endpoint_non_compute'}
})
class SSXGatherData(GladierBaseTool):

    flow_input = {
        'metadata': {
            "description": "Automated data processing.",
            "creators": [{"creatorName": "Kanzus"}],
            "publisher": "Automate",
            "subjects": [{"subject": "SSX"}],
            "publicationYear": '2021',
        }
    }

    required_input = [
        'trigger_name',
        'proc_dir',
        'upload_dir',
        'funcx_endpoint_non_compute',
    ]

    funcx_functions = [
        ssx_gather_data
    ]


