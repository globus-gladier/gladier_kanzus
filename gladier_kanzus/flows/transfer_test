flow_definition = {
  "Comment": "An analysis flow",
  "StartAt": "Transfer",
  "States": {
    "Transfer": {
      "Comment": "Initial transfer",
      "Type": "Action",
      "ActionUrl": "https://actions.automate.globus.org/transfer/transfer",
      "ActionScope": "https://auth.globus.org/scopes/actions.globus.org/transfer/transfer",
      "Parameters": {
        "source_endpoint_id.$": "$.input.source_endpoint", 
        "destination_endpoint_id.$": "$.input.dest_endpoint",
        "transfer_items": [
          {
            "source_path.$": "$.input.source_path",
            "destination_path.$": "$.input.dest_path",
            "recursive": False
          }
        ]
      },
      "ResultPath": "$.Transfer1Result",
      "WaitTime": 600,
      "Next": "Analyze"
    },