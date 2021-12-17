# pip install gladier
from gladier import GladierBaseClient, generate_flow_definition, GladierBaseTool

def generate_transfer_block(**data):
    import pathlib
    destination_prefix = pathlib.Path(data['transfer_block_destination'])
    transfer_items = [
        {
            'source_path': path,
            'destination_path': str(destination_prefix / pathlib.Path(path).name),
            'recursive': False
        } for path in data['transfer_block_source_paths']
    ]
    return transfer_items

class TransferBlock(GladierBaseTool):
    """
    Transfer Block is a funcx function coupled with a Globus Transfer. The funcx function
    generates the input which is then passed to the transfer state. This allows the generate_transfer_block
    function to generate an arbitrary list of files. 
    """
    flow_definition = {
        'Comment': 'Transfer a file or directory in Globus',
        'StartAt': 'GenerateTransferBlock',
        'States': {
            'GenerateTransferBlock': {
                'ActionScope': 'https://auth.globus.org/scopes/b3db7e59-a6f1-4947-95c2-59d6b7a70f8c/action_all',
                'ActionUrl': 'https://automate.funcx.org',
                'Comment': None,
                'Next': 'TransferBlock',
                'ExceptionOnActionFailure': True,
                'Parameters': {'tasks': [{'endpoint.$': '$.input.funcx_endpoint_non_compute',
                                          'function.$': '$.input.generate_transfer_block_funcx_id',
                                          'payload.$': '$.input'}]},
                'ResultPath': '$.GenerateTransferBlock',
                'Type': 'Action',
                'WaitTime': 300
            },
            'TransferBlock': {
                'Comment': 'Transfer a file or directory in Globus',
                'Type': 'Action',
                'ActionUrl': 'https://actions.automate.globus.org/transfer/transfer',
                'Parameters': {
                    'source_endpoint_id.$': '$.input.transfer_block_source_endpoint_id',
                    'destination_endpoint_id.$': '$.input.transfer_block_destination_endpoint_id',
                    'transfer_items.$': '$.GenerateTransferBlock.details.result[0]',
                },
                'ResultPath': '$.Transfer',
                'WaitTime': 600,
                'End': True
            },
        }
    }
    funcx_functions = [generate_transfer_block]
    required_input = [
        'funcx_endpoint_non_compute',
        'transfer_block_source_endpoint_id',
        'transfer_block_destination_endpoint_id',
        'transfer_block_source_paths',
        'transfer_block_destination',
    ]
    flow_input = {}



# from pprint import pprint

# # Test in a client
# @generate_flow_definition
# class TransferBlock(GladierBaseClient):
#     gladier_tools = [
#         TransferBlock,
#     ]

# tb = TransferBlock()
# flow_input = {
#     'input': {
#         'funcx_endpoint_non_compute': '4b116d3c-1703-4f8f-9f6f-39921e5864df',
#         'transfer_block_source_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
#         # By default, this will transfer the encrypt file to Globus Tutorial Endpoint 1
#         'transfer_block_destination_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
#         'transfer_block_source_paths': ['/share/godata/file1.txt'],
#         'transfer_block_destination': '~/',
#     }
# }
# flow = tb.run_flow(flow_input=flow_input)
# tb.progress(flow['run_id'])
# pprint(tb.get_status(flow['run_id']))