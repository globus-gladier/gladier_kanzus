import os, glob, shutil, time



folder = '/ssx/O'
new_folder = '/ssx/O_new'
delta = 0.1
f_list = sorted(glob.glob(os.path.join(folder,'*.cbf')))

os.makedirs(new_folder, exist_ok=True)

for kfile in f_list:
    time.sleep(delta)
    fname = os.path.basename(kfile)
    new_path = os.path.join(new_folder,fname)
    print(kfile)
    print(new_path)
    shutil.copyfile(kfile,new_path)
