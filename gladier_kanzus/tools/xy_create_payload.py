from gladier import GladierBaseTool, generate_flow_definition

def xy_create_payload(**data):
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
    local_ep = data.get('funcx_endpoint_non_compute')
    queue_ep = data.get('funcx_endpoint_compute')
    stills_cont_fxid = data.get("stills_process_funcx_id")
    funcx_create_phil_funcx_id = data.get("create_phil_funcx_id")

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
                del(payload['funcx_endpoint_compute'])
                del(payload['stills_process_funcx_id'])
                del(payload['create_phil_funcx_id'])
            except:
                pass

            phil_task = { 
                "endpoint": local_ep,
                "function": funcx_create_phil_funcx_id,
                "payload": payload
            }
            stills_task = { 
                "endpoint": queue_ep,
                "function": stills_cont_fxid,
                "payload": payload
            }
            
            inputs['phils']['tasks'].append(phil_task)
            inputs['stills']['tasks'].append(stills_task)

    return inputs

@generate_flow_definition
class XYSearch(GladierBaseTool):
    funcx_functions = [xy_create_payload]
