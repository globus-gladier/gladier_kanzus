from gladier import GladierBaseTool, generate_flow_definition

def wait_trigger_file(**data):
    import os
    import time
    data_dir = data['data_dir']
    filename = data["filename"]
    
    trigger_file = os.path.join(data_dir,filename)

    while not os.path.exists(trigger_file):
        time.sleep(5)
        
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
