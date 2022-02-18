from gladier import GladierBaseTool, generate_flow_definition

def dials_stills(**data):
    """Run dials-stills
    Variables:
    - data['data_dir'] is the path where the raw (cbf) data is stored
    - data['proc_dir'] is the path to where dials will run and save results
    - data['run_num'] set the beamline json and phil being used
    - data['cbf_num'] gives the # of the trigger for this flow
    - data['stills_batch_size'] gives the ammount of cbf's processed on this instance
    Optional variables can be passed to overwrite the default values
    - data['dials_path'] can be set for different installations (the container always have a link at '/')
    - data['timeout'] can be set for faster/slower failure
    """
    import os
    import subprocess

    data_dir = data['data_dir']
    proc_dir = data['proc_dir']
    run_num = data['run_num']
    chip_name = data['chip_name']
    cbf_num = data['cbf_num']
    batch_size = data['stills_batch_size']

    phil_name = f"{proc_dir}/process_{run_num}.phil"

    cbf_start = cbf_num - batch_size + 1
    cbf_end = cbf_num

    input_files = f"{chip_name}_{run_num}_{{{str(cbf_start).zfill(5)}..{str(cbf_end).zfill(5)}}}.cbf"

    timeout = data.get('timeout', 1200)

    logname = 'log-' + data['filename'].replace('.cbf','')
    
    dials_path = data.get('dials_path','/dials')
    cmd = f'source {dials_path}/dials && timeout {timeout} dials.stills_process {phil_name} {data_dir}/{input_files} > {logname}.txt'

    os.chdir(proc_dir) 
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=True, executable='/bin/bash')
    
    return cmd, str(res.stdout), str(res.stderr)


@generate_flow_definition(modifiers={
    'dials_stills': {'WaitTime':7200}
})
class DialsStills(GladierBaseTool):
    flow_input = {}
    required_input = [
        'data_dir',
        'proc_dir',
        'run_num',
        'chip_name',
        'cbf_num',
        'stills_batch_size',
        'funcx_endpoint_compute',
    ]
    funcx_functions = [dials_stills]
