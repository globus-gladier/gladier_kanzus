from gladier import GladierBaseTool, generate_flow_definition

def dials_stills(**data):
    import os
    import subprocess

    proc_dir = data['proc_dir']
    data_dir = data['data_dir']
    run_num = data['run_num']
    chip_name = data['chip_name']
    cbf_num = data['cbf_num']
    batch_size = data['stills_batch_size']

    phil_name = f"{proc_dir}/process_{run_num}.phil"

    cbf_start = cbf_num - batch_size
    cbf_end = cbf_num - 1

    file_start = f"{chip_name}_{run_num}_{cbf_start}.cbf"
    file_end = f"{chip_name}_{run_num}_{cbf_end}.cbf"

    input_files = f"{chip_name}_{run_num}_{{{str(cbf_start).zfill(5)}..{str(cbf_end).zfill(5)}}}.cbf"

    timeout = data.get('timeout', 1200)

    logname = 'log-' + data['filename'].replace('.cbf','')
    
    dials_path = data.get('dials_path','')
    cmd = f'source {dials_path}/dials_env.sh && timeout {timeout} dials.stills_process {phil_name} {data_dir}/{input_files} > {logname}.txt'

    os.chdir(proc_dir) 
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=True, executable='/bin/bash')
    
    return cmd, str(res.stdout)


@generate_flow_definition(modifiers={
    'dials_stills': {'WaitTime':7200}
})
class DialsStills(GladierBaseTool):
    funcx_functions = [dials_stills]
