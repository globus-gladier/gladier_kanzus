import pathlib
import os
import time
import sys

dirname = sys.argv[1]
num = sys.argv[2]
print(f'Checking {dirname} for multiples of {num}')

for idx, path in enumerate(os.listdir(dirname)):
    if '.cbf' in path:
        try:
            cbfnum = path.split("_")[-1][:-4]
            if int(cbfnum) % 256 == 0:
                #print(cbfnum)
                #print(path)
                pathlib.Path(f'{dirname}{path}').touch()
                print(f'touch {dirname}{path}')
                time.sleep(5)
        except:
            print(f'path failure {path}')
