flow_definition = {
  "Comment": "Kanzus Phils Flow",
  "StartAt": "create_input",
  "States": {
      "create_input": {
      "Comment": "Create input for the search",
      "Type": "Action",
      "ActionUrl": "https://api.funcx.org/automate",
      "ActionScope": "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all",
      "Parameters": {
          "tasks": [{
            "endpoint.$": "$.input.funcx_local_ep",
            "func.$": "$.input.xy_search_funcx_id",
            "payload.$": "$.input"
        }]
      },
      "ResultPath": "$.Exec1Result",
      "WaitTime": 600,
      "Next": "create_phil"
    },
    "create_phil": {
      "Comment": "Create Dials Phil",
      "Type": "Action",
      "ActionUrl": "https://api.funcx.org/automate",
      "ActionScope": "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all",
      "InputPath": "$.Exec1Result.details.result.phils",
      "ResultPath": "$.Exec2Result",
      "WaitTime": 600,
      "Next": "run_stills"
    },
    "run_stills": {
      "Comment": "Dials Stills Function",
      "Type": "Action",
      "ActionUrl": "https://api.funcx.org/automate",
      "ActionScope": "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all",
      "InputPath": "$.Exec1Result.details.result.stills",
      "ResultPath": "$.Exec2Result",
      "WaitTime": 3600,
      "Next": "plot_search"
    },
    "plot_search": {
      "Comment": "Plot the search results",
      "Type": "Action",
      "ActionUrl": "https://api.funcx.org/automate",
      "ActionScope": "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all",
      "Parameters": {
          "tasks": [{
            "endpoint.$": "$.input.funcx_local_ep",
            "func.$": "$.input.xy_plot_funcx_id",
            "payload.$": "$.input"
        }]
      },
      "ResultPath": "$.Exec4Result",
      "WaitTime": 600,
      "End": True
    }
  }
}