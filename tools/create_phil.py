def funcx_create_phil(data):
    """Create a phil file if one doesn't already exist"""
    import json
    import os
    from string import Template

    proc_dir = data['proc_dir']
    data_dir = os.path.split(data['input_files'])[0]
    run_num = data['input_files'].split("_")[-2]
    
    
    if 'suffix' in data:
        phil_name = f"{proc_dir}/process_{run_num}_{data['suffix']}.phil"
    else:
        phil_name = f"{proc_dir}/process_{run_num}.phil"

    
    unit_cell = data.get('unit_cell', None)
    
    ##opening existing files
    beamline_json = os.path.join(data_dir,f"beamline_run{run_num}.json")
    mask = os.path.join(data_dir,data.get('mask', 'mask.pickle'))

    beamline_data = None

    try:
        with open(beamline_json, 'r') as fp:
            beamline_data = json.loads(fp.read())

        if not unit_cell:
            unit_cell = beamline_data['user_input']['unit_cell']

        unit_cell = unit_cell.replace(",", " ")
        space_group = beamline_data['user_input']['space_group']
        det_distance = float(beamline_data['beamline_input']['det_distance']) * -1.0
    except:
        pass

    template_data = {'det_distance': det_distance,
                     'unit_cell': unit_cell,
                     'nproc': data['nproc'],
                     'space_group': space_group,
                     'beamx': data['beamx'],
                     'beamy': data['beamy'],
                     'mask': mask}

    template_phil = Template("""spotfinder.lookup.mask=$mask
integration.lookup.mask=$mask
spotfinder.filter.min_spot_size=2
significance_filter.enable=True
#significance_filter.isigi_cutoff=1.0
mp.nproc = $nproc
mp.method=multiprocessing
refinement.parameterisation.detector.fix=none
geometry {
  detector {
      panel {
                fast_axis = 0.9999673162585729, -0.0034449798523932267, -0.007314268824966957
                slow_axis = -0.0034447744696749034, -0.99999406591948, 4.0677756813531234e-05
                origin    = $beamx, $beamy, $det_distance
                }
            }
         }
indexing {
  known_symmetry {
    space_group = $space_group
    unit_cell = $unit_cell
  }
  stills.indexer=stills
  stills.method_list=fft1d
  multiple_lattice_search.max_lattices=3
}""")
    phil_data = template_phil.substitute(template_data)

    if not os.path.exists(proc_dir):
        os.mkdir(proc_dir)
        
    with open(phil_name, 'w') as fp:
        fp.write(phil_data)
    return phil_name
