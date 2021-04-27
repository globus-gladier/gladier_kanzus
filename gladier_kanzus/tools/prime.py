def funcx_prime(data):
    """Run the PRIME tool on the int-list.
    - Change dir to the <exp>_prime directory
    - Create phil file for prime.run
    - Call prime.run and pipe the log into a file using the input_range
    - cp the prime's log into the images dir
    - zip the prime dir and copy that into the images dir"""
    import os
    import json
    import shutil
    import subprocess
    from subprocess import PIPE
    from zipfile import ZipFile
    from string import Template

    run_num = data['input_files'].split("/")[-1].split("_")[1]
#run_num = data['input_files'].split("_")[1]
    run_dir = "/".join(data['input_files'].split("/")[:-1])
    exp_name = data['input_files'].split("/")[-1].split("_")[0]
    proc_dir = f'{run_dir}/{exp_name}_processing'
    prime_dir = f'{run_dir}/{exp_name}_prime'
    unit_cell = data.get('unit_cell', None)
    os.chdir(run_dir)

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

    int_file = f"{run_dir}/{exp_name}_images/{exp_name}_ints.txt"
    dmin = "2.1"
    if "dmin" in data:
        dmin = data['dmin']

    prime_run_name = f"{exp_name}_{data['input_range']}"
    template_data = {"dmin": dmin, "int_file": int_file, "unit_cell": unit_cell,
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
    cmd = f"source {dials_path}/dials_env.sh; prime.run prime.phil > {data['input_range']}.log &"
    res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE,
                         shell=True, executable='/bin/bash')

    # make a zip and cp it to images
    shutil.make_archive(prime_run_name, 'zip', prime_run_name)
    shutil.copyfile(f"{prime_run_name}.zip", f"../{exp_name}_images/prime.zip")

    # Also copy the log.txt file
    shutil.copyfile(f"{prime_run_name}/log.txt", f"../{exp_name}_images/prime_log.txt")
    return 'done'

