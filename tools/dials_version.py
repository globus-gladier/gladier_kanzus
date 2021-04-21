def dials_version(data):
    import subprocess
    from subprocess import PIPE
    
    dials_path = data.get('dials_path','')
    cmd = "source {dials_path}/dials_env.sh && dials.version"
    
    res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE,
                             shell=True, executable='/bin/bash')
    return res.stdout
