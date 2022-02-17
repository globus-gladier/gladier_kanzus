
from gladier import GladierBaseTool


class TransferOut(GladierBaseTool):

    flow_definition = {
        'Comment': 'Transfer a file or directory in Globus',
        'StartAt': 'TransferOut',
        'States': {
      "TransferOut": {
      "Comment": "Initial transfer",
      "Type": "Action",
      "ActionUrl": "https://actions.automate.globus.org/transfer/transfer",
      "Parameters": {
        "source_endpoint_id.$": "$.input.globus_local_ep", 
        "destination_endpoint_id.$": "$.input.globus_dest_ep",
        "sync_level": 1,
        "transfer_items": [
          {
            "source_path.$": "$.input.local_data_dir",
            "destination_path.$": "$.input.data_dir",
            "recursive": True
          }
        ]
      },
      "ResultPath": "$.TransferData",
      "WaitTime": 600,
                'End': True
            },
        }
    }

    flow_input = {}
