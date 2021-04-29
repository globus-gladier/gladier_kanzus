
def xy_search(data):
    """Create funcX inputs for the phil and stills tools
    for a range of beamx/y values.
    """
    import copy
    import numpy as np

    sig_figs = data.get("sig_figs", 1)
    span = float(data.get("span", 1.0))
    span_half = span / 2
    step = float(data.get("step", 0.1))
    beamx = float(data.get("beamx"))
    beamy = float(data.get("beamy"))
    local_ep = data.get('funcx_local_ep')
    queue_ep = data.get('funcx_queue_ep')
    stills_cont_fxid = data.get("stills_cont_fxid")
    funcx_create_phil_funcx_id = data.get("funcx_create_phil_funcx_id")

    x_values = np.round(np.arange(beamx - span_half, beamx + span_half + step, step), decimals=sig_figs)
    y_values = np.round(np.arange(beamy - span_half, beamy + span_half + step, step), decimals=sig_figs)

    inputs = {'phils': {"tasks": []}, 'stills': {"tasks": []}}

    # Create phils inputs
    for x in x_values:
        for y in y_values:
            payload = copy.deepcopy(data)
            payload['proc_dir'] = data['proc_dir'] + f"{x}_{y}"
            payload['beamx'] = x
            payload['beamy'] = y
            
            try:
                del(payload['span'])
                del(payload['step'])
                del(payload['sig_figs'])
                del(payload['spfuncx_local_epan'])
                del(payload['funcx_queue_ep'])
                del(payload['stills_cont_fxid'])
                del(payload['funcx_create_phil_funcx_id'])
            except:
                pass

            phil_task = { 
                "endpoint": local_ep,
                "func": funcx_create_phil_funcx_id,
                "payload": payload
            }
            stills_task = { 
                "endpoint": queue_ep,
                "func": stills_cont_fxid,
                "payload": payload
            }
            
            inputs['phils']['tasks'].append(phil_task)
            inputs['stills']['tasks'].append(stills_task)

    return inputs