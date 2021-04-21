def funcx_stills_process(data):
    import os
    import subprocess
    from distutils.dir_util import copy_tree
    from subprocess import PIPE

    
    proc_dir = data['proc_dir']
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
    cmd = f'source {dials_path}/dials_env.sh && dials.stills_process {phil_name} {input_files} > log-{file_end}.txt'

    
    os.chdir(proc_dir) ##Need to guarantee the worker is at the correct location..
    res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE,
                             shell=True, executable='/bin/bash')
    
    return str(res.stdout)

def funcx_plot_ssx(data):
    import os
    import json
    import shutil
    import glob
    import subprocess
    import numpy as np
    from subprocess import PIPE
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm


    data_dir = data['data_dir']
    proc_dir = data['proc_dir']
    data_dir = os.path.split(data['input_files'])[0]
    run_num = data['input_files'].split("_")[-2]
    
    
    if 'suffix' in data:
        phil_name = f"{proc_dir}/process_{run_num}_{data['suffix']}.phil"
    else:
        phil_name = f"{proc_dir}/process_{run_num}.phil"


    ##opening existing files
    beamline_json = os.path.join(data_dir,f"beamline_run{run_num}.json")

    beamline_data = None
    with open(beamline_json, 'r') as fp:
        beamline_data = json.loads(fp.read())

    xdim = int(beamline_data['user_input']['x_num_steps'])
    ydim = int(beamline_data['user_input']['y_num_steps'])

    # Get the list of int files in this range
    int_files = glob.glob(os.path.join(proc_dir,'int-*.pickle'))

    ##########
    #lattice_counts = get_lattice_counts(xdim, ydim, int_files)
    ##########
    lattice_counts = np.zeros(xdim*ydim)
    for int_file in int_files:
        int_file = int_file.rstrip('.pickle\n')
        index = int(int_file.split('_')[-1])
        lattice_counts[index] += 1

    lattice_counts = lattice_counts.reshape((ydim, xdim))
    # reverse the order of alternating rows
    lattice_counts[1::2, :] = lattice_counts[1::2, ::-1]
    
  
    plot_name = f'1int-sinc-{data["input_range"]}.png'

    ########
    #plot_lattice_counts(xdim, ydim, lattice_counts, plot_name)
    ########

    fig = plt.figure(figsize=(xdim/10., ydim/10.))
    plt.axes([0, 0, 1, 1])  # Make the plot occupy the whole canvas
    plt.axis('off')
    plt.imshow(lattice_counts, cmap='hot', interpolation=None, vmax=4)
    plt.savefig(plot_name)


    exp_name = data['input_files'].split("/")[-1].split("_")[0]

    # create an images directory
    image_dir = f"{proc_dir}/{exp_name}_images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    int_file = f"{image_dir}/{exp_name}_ints.txt"
    with open(int_file, 'w+') as fp:
        fp.write("\n".join(i for i in int_files))

    os.chdir(image_dir)

    dials_path = data.get('dials_path','')
    cmd = f"source {dials_path}/dials_env.sh && \
        dials.unit_cell_histogram ../{proc_dir}_processing/*integrated_experiments.json"

    subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, executable='/bin/bash')

    return plot_name

