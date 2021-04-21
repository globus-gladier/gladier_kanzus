def create_flow_tasks(self, payload, funcx_worker, funcx_login=None):
        """
        'funcx_phil': payload,
        'funcx_stills': stills_payload,
        'funcx_plot': payload,
        'funcx_pilot': payload,
        'funcx_prime': payload,
        """
        if funcx_login is None:
            funcx_login = funcx_worker
        return {
            "Transfer1Input": payload['transfer'],
            "Exec1Input": {
                "tasks": [{
                    "endpoint": funcx_worker,
                    "func": self.fxid_phil,
                    "payload": payload['funcx_phil']
                }]
            },
            "Exec2Input": {
                "tasks": [{
                    "endpoint": funcx_worker,
                    "func": self.fxid_stills,
                    "payload": p
                } for p in payload['funcx_stills']]
            },
            "Exec3Input": {
                "tasks": [{
                    "endpoint": funcx_worker,
                    "func": self.fxid_plot,
                    "payload": payload['funcx_plot']
                }]
            },
            "Exec4Input": {
                "tasks": [{
                    "endpoint": funcx_worker,
                    "func": self.fxid_prime,
                    "payload": payload['funcx_prime']
                }]
            },
            "Exec5Input": {
                "tasks": [{
                    "endpoint": funcx_login,
                    "func": self.fxid_pilot,
                    "payload": payload['funcx_pilot']
                }]
            }
        }