from gladier import GladierBaseTool


class TransferProc(GladierBaseTool):

    flow_definition = {
        'Comment': 'Transfer a file or directory in Globus',
        'StartAt': 'TransferProc',
        'States': {
            "TransferProc": {
      "Comment": "Data back transfer",
      "Type": "Action",
      "ActionUrl": "https://actions.automate.globus.org/transfer/transfer",
      "Parameters": {
        "source_endpoint_id.$": "$.input.globus_dest_ep", 
        "destination_endpoint_id.$": "$.input.globus_local_ep",
        "sync_level": 1,
        "transfer_items": [
          {
            "source_path.$": "$.input.proc_dir",
            "destination_path.$": "$.input.local_proc_dir",
            "recursive": True
          }
        ]
      },
      "ResultPath": "$.TransferProc",
      "WaitTime": 600,
                'End': True
            },
        }
    }

    flow_input = {}