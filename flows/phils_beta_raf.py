flow_definition = {
  "Comment": "Kanzus Phils Flow",
  "StartAt": "Dials Create Phil",
  "States": {
    "Dials Create Phil": {
      "Comment": "Create Dials Phil",
      "Type": "Action",
      "ActionUrl": "https://api.funcx.org/automate",
      "ActionScope": "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all",
      "Parameters": {
          "tasks": [{
            "endpoint.$": "$.input.funcx_ep",
            "func.$": "$.input.funcx_create_phil_funcx_id",
            "payload.$": "$.input"
        }]
      },
      "ResultPath": "$.Exec1Result",
      "WaitTime": 600,
      "Next": "Dials Stills"
    },
    "Dials Stills": {
      "Comment": "Dials Stills Function",
      "Type": "Action",
      "ActionUrl": "https://api.funcx.org/automate",
      "ActionScope": "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all",
      "Parameters": {
          "tasks": [{
            "endpoint.$": "$.input.funcx_ep",
            "func.$": "$.input.funcx_stills_process_funcx_id",
            "payload.$": "$.input"
        }]
      },
      "ResultPath": "$.Exec5Result",
      "WaitTime": 600,
      "End": True
    }
  }
}