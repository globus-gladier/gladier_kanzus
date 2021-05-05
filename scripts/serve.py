import os
import glob
import shutil
import time
import argparse

def create_experiment(sample_name, target_folder):
    
    ##folowing beamline structure with first letter of sample name
    exp_name = sample_name[0]

    f_path = os.path.join(target_folder,exp_name)
    
    print('Creating experiment')
    print('  Sample name: ' + sample_name)
    print('  Location: ' + f_path)
    if os.path.isdir(f_path):
        print('  Folder already existed!')
    print('')

    os.makedirs(f_path, exist_ok=True)

    return f_path

def serve_experiment(exp_path, serve_folder, std_folder, delta=0.1, n_files=2048):

    f_list = sorted(glob.glob(os.path.join(serve_folder,'*.cbf')))

    shutil.copytree(std_folder,exp_path,dirs_exist_ok=True)
    print('Serving experimental files')
    print(' From: ' + serve_folder)
    print(' Exp folder: ' + exp_path)
    print(' Std files: ' + std_folder)
    print('')
    

    for  _ , kfile in enumerate(f_list):
        fname = os.path.basename(kfile)
        new_path = os.path.join(exp_path,fname)
        print(new_path)
        shutil.copyfile(kfile,new_path)
        time.sleep(delta)


##Arg Parsing
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--samplename', type=str, default='Ohakune')
    parser.add_argument('--workdir', type=str, default='/ssx/workshop/virtual_exp')
    parser.add_argument('--gpdfolder',type=str, default='/ssx/workshop/original_files/O')
    parser.add_argument('--stdfolder',type=str, default='/ssx/workshop/original_files/std_files')
    parser.add_argument('--delta', type=float, default=0.1)
    parser.add_argument('--n_files', type=int, default=2048)
    return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()

    f_path = create_experiment(sample_name=args.samplename, target_folder=args.workdir)
    
    serve_experiment(f_path, args.gpdfolder, args.stdfolder, delta=args.delta, n_files=args.n_files)
