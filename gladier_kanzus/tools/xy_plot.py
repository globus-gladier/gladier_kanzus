def xy_plot(data):
    """Count the number of ints in the proc dirs and plot them"""
    import matplotlib.pyplot as plt
    import seaborn as sb
    import pandas as pd
    import glob
    import os

    data_dir = data['data_dir']
    upload_dir = data.get('upload_dir', '')
    os.chdir(data_dir)

    dirs = glob.glob('xy-*')

    data = {'X': [], 'Y': [], 'Ints': []}
    for dir_name in dirs:
        try:
            x, y = dir_name[3:].split("_")
            ints = len(glob.glob(f"{dir_name}/int-*"))
            data['X'].append(float(x))
            data['Y'].append(float(y))
            data['Ints'].append(ints)
        except:
            pass

    df = pd.DataFrame(data)
    table = df.pivot('Y', 'X', 'Ints')
    ax = sb.heatmap(table, linewidths=0.5, cmap="Blues")
    ax.invert_yaxis()
    plt.savefig(f'{upload_dir}/xysearch.png', bbox_inches='tight', dpi=100)