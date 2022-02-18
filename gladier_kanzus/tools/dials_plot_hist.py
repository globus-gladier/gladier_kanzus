from gladier import GladierBaseTool, generate_flow_definition

def dials_plot_hist(**data):
    """Run the DIALS Plot histogram tool on the proc_dir.
    - Change dir to the <exp>_prime directory
    Variables:
    - data['proc_dir'] is the path to where dials saved the processed files.
    - data['upload_dir'] is the path which will be published in the portal
    Optional Variables:
    - data['dials_path'] can be set for different installations (the container always have a link at '/')
    """
    import os
    import subprocess
    from subprocess import PIPE

    proc_dir = data['proc_dir']
    upload_dir = data['upload_dir']

    os.chmod(upload_dir)
    dials_path = data.get('dials_path','/dials')
    cmd = f"source {dials_path}/dials && dials.unit_cell_histogram {proc_dir}*integrated.expt"

    res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, executable='/bin/bash')

    return res.stdout, res.stderr

@generate_flow_definition(modifiers={
    'dials_stills': {'WaitTime':7200}
})
class DialsPlotHist(GladierBaseTool):
    flow_input = {}
    required_input = [
        'proc_dir',
        'upload_dir',
        'funcx_endpoint_compute',
    ]
    funcx_functions = [dials_plot_hist]
