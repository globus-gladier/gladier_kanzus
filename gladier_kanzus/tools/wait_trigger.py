from gladier import GladierBaseTool, generate_flow_definition

def wait_trigger_file(**data):
    import os

    data_dir = data['data_dir']
    trigger_name = data["input"]["trigger_name"]
    trigger_file = os.path.join(data_dir,os.path.basename(trigger_name))

    while not os.path.exists(trigger_file):
        pass

    return trigger_name

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
