from gladier import GladierBaseTool


class TransferImage(GladierBaseTool):

    flow_definition = {
        'Comment': 'Transfer a file or directory in Globus',
        'StartAt': 'TransferImage',
        'States': {
          "TransferImage": {
      "Comment": "Data back transfer",
      "Type": "Action",
      "ActionUrl": "https://actions.automate.globus.org/transfer/transfer",
      "Parameters": {
        "source_endpoint_id.$": "$.input.globus_dest_ep", 
        "destination_endpoint_id.$": "$.input.globus_local_ep",
        "sync_level": 1,
        "transfer_items": [
          {
            "source_path.$": "$.input.upload_dir",
            "destination_path.$": "$.input.local_upload_dir",
            "recursive": True
          }
        ]
      },
      "ResultPath": "$.TransferImage",
      "WaitTime": 600,
                'End': True
            },
        }
    }

    flow_input = {}
