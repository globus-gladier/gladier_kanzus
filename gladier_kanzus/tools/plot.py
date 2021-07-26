from typing import List
from gladier import GladierBaseTool, generate_flow_definition


def ssx_plot(xdim: int, ydim: int, int_indices: List[int], plot_filename: str):
    """
    Plot the current list of ints so far. Data requires the following keys
        * xdim (int) X dimension for the plot
        * ydim (int) Y dimension for the plot
        * int_indices (list of ints) list of int 'hits' to light up on the plot
        * plot_name (path) full filename to save the plot
    """
    import numpy as np
    from matplotlib import pyplot as plt

    lattice_counts = np.zeros(xdim*ydim, dtype=np.dtype(int))
    for index in int_indices:
        lattice_counts[index] += 1
    lattice_counts = lattice_counts.reshape((ydim, xdim))
    # reverse the order of alternating rows
    lattice_counts[1::2, :] = lattice_counts[1::2, ::-1]

    # plot the lattice counts
    plt.figure(figsize=(xdim/10., ydim/10.))
    plt.axes([0, 0, 1, 1])  # Make the plot occupy the whole canvas
    plt.axis('off')
    plt.imshow(lattice_counts, cmap='hot', interpolation=None, vmax=4)
    plt.savefig(plot_filename)


@generate_flow_definition
class SSXPlot(GladierBaseTool):

    flow_input = {}

    required_input = [
        'funcx_endpoint_compute',
    ]

    funcx_functions = [
        ssx_plot,
    ]
