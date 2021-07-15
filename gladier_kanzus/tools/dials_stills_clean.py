from gladier import GladierBaseTool, generate_flow_definition

def funcx_stills_process(**data):
    import os
    import subprocess
    from distutils.dir_util import copy_tree
    from subprocess import PIPE

    
    proc_dir = data['proc_dir']
    data_dir = data['data_dir']
    input_files = data['input_files']
    run_num = data['input_files'].split("_")[-2]
    
    if 'suffix' in data:
        phil_name = f"{proc_dir}/process_{run_num}_{data['suffix']}.phil"
    else:
        phil_name = f"{proc_dir}/process_{run_num}.phil"

    file_end = data['input_range'].split("..")[-1]
  
    if not "timeout" in data:
        data["timeout"] = 0

    dials_path = data.get('dials_path','')
    cmd = f'source {dials_path}/dials_env.sh && timeout 300 dials.stills_process {phil_name} {data_dir}/{input_files} > log-{file_end}.txt'

    
    os.chdir(proc_dir) ##Need to guarantee the worker is at the correct location..
    res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE,
                             shell=True, executable='/bin/bash')
    
    return str(res.stdout)
