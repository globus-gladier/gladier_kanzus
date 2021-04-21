from gladier.defaults import GladierDefaults


def ssx_plot(data):
    import os
    import json
    import shutil
    import subprocess
    from subprocess import PIPE
    from zipfile import ZipFile
    from Kanzus.tools.plot_ints import get_dims, get_lattice_counts, plot_lattice_counts

    # get the x/y dims
    run_num = data['input_files'].split("/")[-1].split("_")[1]
#run_num = data['input_files'].split("_")[1]
    run_dir = "/".join(data['input_files'].split("/")[:-1])
    exp_name = data['input_files'].split("/")[-1].split("_")[0]
    proc_dir = f'{run_dir}/{exp_name}_processing'

    os.chdir(run_dir)

    input_parent = "/".join(run_dir.split("/")[:-1])
    sample_file = f"{run_dir}/sample{run_num}.json"
    phil_name = f"{run_dir}/process_{run_num}.phil"
    beamline_json = f"beamline_run{run_num}.json"
    beamline_data = None

    if not os.path.exists(beamline_json):
        return f'{beamline_json} file does not exist!'

    with open(beamline_json, 'r') as fp:
        beamline_data = json.loads(fp.read())

    xdim = int(beamline_data['user_input']['x_num_steps'])
    ydim = int(beamline_data['user_input']['y_num_steps'])

    # os.chdir(process_dir)

    # Get the list of int files in this range
    int_files = []
    start, end = data['input_range'].split("..")
    int_range = range(int(start), int(end))

    # Get all the int files
    for filename in os.listdir(f'{exp_name}_processing'):
        try:
            if "int-" in filename and ".pickle" in filename:
                int_files.append(f"{proc_dir}/{filename}")
        except:
            pass

    lattice_counts = get_lattice_counts(xdim, ydim, int_files)
    plot_name = f'1int-sinc-{data["input_range"]}.png'
    plot_lattice_counts(xdim, ydim, lattice_counts, plot_name)

    # move the image file up a line
    exp_name = data['input_files'].split("/")[-1].split("_")[0]

    # create an images directory
    image_dir = f"{run_dir}/{exp_name}_images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    int_file = f"{run_dir}/{exp_name}_images/{exp_name}_ints.txt"
    with open(int_file, 'w+') as fp:
        fp.write("\n".join(i for i in int_files))

    zip_name = f'ints-{data["input_range"]}.zip'
    # Create a zip of all the int files
    with ZipFile(zip_name, 'w') as zipObj:
        for int_filename in int_files:
            zipObj.write(int_filename)

    shutil.copyfile(zip_name, f"{image_dir}/ints.zip")
    shutil.copyfile(plot_name, f"{image_dir}/{plot_name}")
    shutil.copyfile(plot_name, f"{image_dir}/composite.png")
    shutil.copyfile(f"{run_dir}/{beamline_json}", f"{image_dir}/{beamline_json}")
    shutil.copyfile(f"{phil_name}", f"{image_dir}/{phil_name.split('/')[-1]}")

    os.chdir(image_dir)

    # cmd = f"dials.unit_cell_histogram ../{exp_name}_processing/*integrated_experiments.json"
    #
    # res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE,
    #                      shell=True, executable='/bin/bash')
    return plot_name


class SSXPlot(GladierDefaults):

    flow_definition = {
      'Comment': 'Plot SSX data',
      'StartAt': 'SSXPlot',
      'States': {
        'SSXPlot': {
          'Comment': 'Upload to petreldata, ingest to SSX search index',
          'Type': 'Action',
          'ActionUrl': 'https://api.funcx.org/automate',
          'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
          'ExceptionOnActionFailure': False,
          'Parameters': {
              'tasks': [{
                'endpoint.$': '$.input.funcx_endpoint_compute',
                'func.$': '$.input.ssx_plot_funcx_id',
                'payload.$': '$.input',
            }]
          },
          'ResultPath': '$.SSXPlot',
          'WaitTime': 600,
          'End': True
        }
      }
    }

    flow_input = {

    }

    required_input = [
        # 'chip',
        # 'experiment_number',
        # 'run_name',
        # 'aps_data',
        # 'trigger_name',
    ]

    funcx_functions = [
        ssx_plot
    ]
