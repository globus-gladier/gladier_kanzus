from gladier import GladierBaseTool, generate_flow_definition

def dials_prime(**data):
    """Run the PRIME tool on the int-list.
    - Change dir to the <exp>_prime directory
    - Create phil file for prime.run
    - Call prime.run with the current list of ints generated
    - (not implemented) cp the prime's log into the images dir
    - (not implemented) zip the prime dir and copy that into the images dir
    Variables:
    - data['proc_dir'] is the path to where dials will run and save results
    - data['prime_dir'] is the path to the folder which prime will run and save results
    - data['exp'] is the experiment name
    - data['run_num'] is the beamline run associated with this sample.
    Optional Variables:
    - data['unit_cell'] sets a new unit cell into the prime-phil
    - data['prime_dmin'] sets the dmin value different than 2.1
    - data['dials_path'] can be set for different installations (the container always have a link at '/')
    """
    import os
    import json
    import subprocess
    from subprocess import PIPE
    from string import Template
    import glob 

    proc_dir = data['proc_dir']
    prime_dir = data['prime_dir']

    run_num = data['run_num']
    exp_name = data['exp']
    
    unit_cell = data.get('unit_cell', None)
    dmin = data.get('prime_dmin', 2.1)

    int_filenames =  sorted(glob.glob(os.path.join(proc_dir,'int-*.pickle')))

    if len(int_filenames)==0:
        return 'no ints'

    if not os.path.exists(prime_dir):
                os.mkdir(prime_dir)

    proc_ints_file = os.path.join(prime_dir,'proc_ints.txt')

    if os.path.exists(proc_ints_file):
        os.remove(proc_ints_file)

    with open(proc_ints_file,'w+') as f:
        for intfile in sorted(int_filenames):
            f.write(str(intfile) + "\n")

    
    prime_run_name = exp_name + '_prime_' + str(len(int_filenames))
    
    os.chdir(prime_dir)

    try:
        beamline_json = f"beamline_run{run_num}.json"
        with open(beamline_json, 'r') as fp:
            beamline_data = json.loads(fp.read())
        if not unit_cell:
            unit_cell = beamline_data['user_input']['unit_cell']
        unit_cell = unit_cell.replace(",", " ")
    except:
        pass

    if not os.path.exists(prime_dir):
        os.makedirs(prime_dir)

    os.chdir(prime_dir)

    template_data = {"dmin": dmin, "int_file": proc_ints_file, "unit_cell": unit_cell,
                     "run_name": prime_run_name}

    template_prime = Template("""data = $int_file 
run_no = $run_name
target_unit_cell = $unit_cell
target_space_group = P3121
n_residues = 415 
pixel_size_mm = 0.172
#This is so you can use prime.viewstats
flag_output_verbose=True
scale {
        d_min = $dmin
        d_max = 50
        sigma_min = 1.5
}
postref {
        scale {
                d_min = $dmin
                d_max = 50
                sigma_min = 1.5
                partiality_min = 0.1
        }
        all_params {
                flag_on = True
                d_min = 1.6
                d_max = 50
                sigma_min = 1.5
                partiality_min = 0.1
                uc_tolerance = 5
        }
}
merge {
        d_min = $dmin
        d_max = 50
        sigma_min = -3.0
        partiality_min = 0.1
        uc_tolerance = 5
}
indexing_ambiguity {
         mode = Auto 
         index_basis_in = None
         assigned_basis = None
         d_min = 3.0
         d_max = 10.0
         sigma_min = 1.5
         n_sample_frames = 1000
         #n_sample_frames = 200
         n_selected_frames = 100
}
n_bins = 20""")

    prime_data = template_prime.substitute(template_data)

    with open('prime.phil', 'w') as fp:
        fp.write(prime_data)

    # run prime
    dials_path = data.get('dials_path','')
    cmd = f"source {dials_path}/dials_env.sh; prime.run prime.phil &"
    subprocess.run(cmd, stdout=PIPE, stderr=PIPE,
                         shell=True, executable='/bin/bash')

    return

@generate_flow_definition
class Prime(GladierBaseTool):
    flow_input = {}
    required_input = [
        'proc_dir',
        'prime_dir',
        'run_num',
        'exp',
        'funcx_endpoint_compute',
    ]
    funcx_functions = [
        dials_prime
    ]
