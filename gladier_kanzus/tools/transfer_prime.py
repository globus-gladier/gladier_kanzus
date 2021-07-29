from gladier import GladierBaseTool


class TransferPrimec(GladierBaseTool):

    flow_definition = {
        'Comment': 'Transfer a file or directory in Globus',
        'StartAt': 'TransferPrime',
        'States': {
            "TransferProc": {
      "Comment": "Prime back transfer",
      "Type": "Action",
      "ActionUrl": "https://actions.automate.globus.org/transfer/transfer",
      "Parameters": {
        "source_endpoint_id.$": "$.input.globus_dest_ep", 
        "destination_endpoint_id.$": "$.input.globus_local_ep",
        "sync_level": 1,
        "transfer_items": [
          {
            "source_path.$": "$.input.prime_dir",
            "destination_path.$": "$.input.local_prime_dir",
            "recursive": True
          }
        ]
      },
      "ResultPath": "$.TransferPrime",
      "WaitTime": 600,
                'End': True
            },
        }
    }

    flow_input = {
        'transfer_sync_level': 'checksum'
    }
    # required_input = [
    #     'transfer_source_path',
    #     'transfer_destination_path',
    #     'transfer_source_endpoint_id',
    #     'transfer_destination_endpoint_id',
    #     'transfer_recursive',
    # ]
