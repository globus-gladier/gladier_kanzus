from gladier import GladierBaseTool, generate_flow_definition

def wait_trigger_file(**data):
    import os
    import time
    data_dir = data['data_dir']
    filename = data['filename']
    run_num = data['run_num']

    trigger_file = os.path.join(data_dir,filename)
    beamline_json = os.path.join(data_dir,f"beamline_run{run_num}.json")

    while not os.path.exists(trigger_file) and not os.path.exists(beamline_json):
        time.sleep(1)
        
    return trigger_file

@generate_flow_definition(modifiers={
    'wait_trigger_file': {'endpoint': 'funcx_endpoint_non_compute'}
})
class WaitTrigger(GladierBaseTool):
    flow_input = {}
    required_input = [
        'funcx_endpoint_non_compute',
    ]
    funcx_functions = [
        wait_trigger_file,
    ]
