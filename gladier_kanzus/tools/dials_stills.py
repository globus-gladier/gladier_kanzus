from gladier import GladierBaseTool, generate_flow_definition

def dials_stills(**data):
    import os
    import subprocess

    proc_dir = data['proc_dir']
    data_dir = data['data_dir']
    input_files = data['input_files']
    run_num = data['run_num']
    
    phil_name = f"{proc_dir}/process_{run_num}.phil"

    file_end = data['input_range'].split("..")[-1]
  
    timeout = data.get('timeout', 1200)

    dials_path = data.get('dials_path','')
    cmd = f'source {dials_path}/dials_env.sh && timeout {timeout} dials.stills_process {phil_name} {data_dir}/{input_files} > log-{file_end}.txt'

    os.chdir(proc_dir) 
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=True, executable='/bin/bash')
    
    return cmd, str(res.stdout)


@generate_flow_definition(modifiers={
    'dials_stills': {'WaitTime':7200}
})
class DialsStills(GladierBaseTool):
    funcx_functions = [dials_stills]
