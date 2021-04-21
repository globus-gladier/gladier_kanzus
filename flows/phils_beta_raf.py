flow_definition = {
  "Comment": "Dials V1 Flow",
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
            "func.$": "$.input.create_phil_fxid",
            "payload.$": "$.input"
        }]
      },
      "ResultPath": "$.Exec4Result",
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
            "func.$": "$.input.stills_fxid",
            "payload.$": "$.input"
        }]
      },
      "ResultPath": "$.Exec5Result",
      "WaitTime": 600,
      "Next": "Plot SSX"
    },
    "Plot SSX": {
      "Comment": "Dials Plot Function",
      "Type": "Action",
      "ActionUrl": "https://api.funcx.org/automate",
      "ActionScope": "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all",
      "Parameters": {
          "tasks": [{
            "endpoint.$": "$.input.funcx_ep",
            "func.$": "$.input.plot_fxid",
            "payload.$": "$.input"
        }]
      },
      "ResultPath": "$.Exec6Result",
      "WaitTime": 600,
      "End": True
    }
  }
}