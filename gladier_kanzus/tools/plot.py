from typing import List
from gladier import GladierBaseTool, generate_flow_definition


def ssx_plot(x_num_steps=0, y_num_steps=0, int_indices=[], plot_filename='composite.png'):
    """
    Plot the current list of ints so far. Data requires the following keys
        * x_num_steps (int) X dimension for the plot
        * y_num_steps (int) Y dimension for the plot
        * int_indices (list of ints) list of int 'hits' to light up on the plot
        * plot_name (path) full filename to save the plot
    """
    import numpy as np
    from matplotlib import pyplot as plt

    lattice_counts = np.zeros(x_num_steps*y_num_steps, dtype=np.dtype(int))
    for index in int_indices:
        lattice_counts[index] += 1
    lattice_counts = lattice_counts.reshape((y_num_steps, x_num_steps))
    # reverse the order of alternating rows
    lattice_counts[1::2, :] = lattice_counts[1::2, ::-1]

    # plot the lattice counts
    plt.figure(figsize=(x_num_steps/10., y_num_steps/10.))
    plt.axes([0, 0, 1, 1])  # Make the plot occupy the whole canvas
    plt.axis('off')
    plt.imshow(lattice_counts, cmap='hot', interpolation=None, vmax=4)
    plt.savefig(plot_filename)
    return plot_filename


@generate_flow_definition(modifiers={
    'ssx_plot': {'endpoint': 'funcx_endpoint_non_compute'}
})
class SSXPlot(GladierBaseTool):

    flow_input = {}

    required_input = [
        'funcx_endpoint_non_compute',
    ]

    funcx_functions = [
        ssx_plot,
    ]
