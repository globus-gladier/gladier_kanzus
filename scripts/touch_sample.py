#!/local/data/idsbc/idstaff/gladier/miniconda3/envs/gladier/bin/python
        
import pathlib
import os
import time
import sys
import argparse

# Arg Parsing
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirname', type=str, default='.')
    parser.add_argument('--mult','-m', type=int, default=512)
    parser.add_argument('--time','-t', type=int, default=1)
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    dirname = args.dirname
    mult = args.mult
    delay = args.time
    print(f'Checking {dirname} for multiples of {mult}')
    #logfile = 'flow_run_log'

    for idx, fname in enumerate(sorted(os.listdir(dirname))):
        if '.cbf' in fname:
            full_path = pathlib.PurePath(dirname,fname)
            try:
                cbfnum = fname.split("_")[-1][:-4]
                if int(cbfnum) % mult == 0:
                    pathlib.Path(full_path).touch()
                    print(f'touch {full_path}')
                    time.sleep(delay)
            except:
                print(f'path failure {full_path}')
