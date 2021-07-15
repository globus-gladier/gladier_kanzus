from gladier import GladierBaseTool, generate_flow_definition

def ssx_publish(**data):
    """
    Upload and ingest SSX metadata to Petrel and Globus Search
    * upload_dir -- The local directory to upload to petrel
    * metadata -- metadata to use for Globus Search
    """
    import pilot.client

    upload_dir = data.get('upload_dir', '')
    assert upload_dir.endswith('_images'), f'Filename "{upload_dir}" DOES NOT appear to be correct'

    pargs = data.get('pilot', {})
    pc = pilot.client.PilotClient()
    assert pc.is_logged_in(), 'Please run `pilot login --no-local-server`'
    assert pc.context.current == pargs.get('context', 'kanzus'), 'Please run `pilot context set kanzus`'
    pc.project.current = pargs.get('project', 'ssx')

    # Set this to the local Globus Endpoint
    local_endpoint = pargs.get('local_endpoint', '08925f04-569f-11e7-bef8-22000b9a448b')
    pc.profile.save_option('local_endpoint', local_endpoint)

    result = pc.upload(upload_dir, '/', metadata=data['metadata'], update=True, skip_analysis=True,
                     dry_run=pargs.get('dry_run', False))
    # These result in lots of output, remove them so they're not in automate
    del result['new_metadata']
    del result['previous_metadata']
    del result['upload']

    return result



class SSXPublish(GladierBaseTool):

    flow_definition = {
      'Comment': 'Run Pilot and upload the result to search + petreldata',
      'StartAt': 'SSXPilot',
      'States': {
        'SSXPilot': {
          'Comment': 'Upload to petreldata, ingest to SSX search index',
          'Type': 'Action',
          'ActionUrl': 'https://api.funcx.org/automate',
          'ActionScope': 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2',
          'ExceptionOnActionFailure': False,
          'Parameters': {
              'tasks': [{
                'endpoint.$': '$.input.funcx_endpoint_non_compute',
                'func.$': '$.input.ssx_pilot_funcx_id',
                'payload.$': '$.input',
            }]
          },
          'ResultPath': '$.SSXPilot',
          'WaitTime': 600,
          'End': True
        }
      }
    }

    flow_input = {}

    required_input = []

    funcx_functions = [
        ssx_publish
    ]

