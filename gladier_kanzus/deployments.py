import datetime
import copy


class BaseDeployment:
    globus_endpoints = dict()
    funcx_endpoints = dict()
    flow_input = dict()

    def get_input(self):
        fi = self.flow_input.copy()
        fi['input'].update(self.funcx_endpoints)
        fi['input'].update(self.globus_endpoints)
        return fi

class RafProd(BaseDeployment):

    globus_endpoints = {
    'beamline_globus_ep' : 'c7e7f102-2166-11ec-8338-9d23a2dd9550',
    'eagle_globus_ep' : '05d2c76a-e867-4f67-aa57-76edeb0beda0',
    'theta_globus_ep': '08925f04-569f-11e7-bef8-22000b9a448b',
    'ssx_eagle_globus_ep' :'4340775f-4758-4fd6-a7b1-990f82aef5de'
    }

    funcx_endpoints = {
        'funcx_endpoint_non_compute' : 'e449e8b8-e114-4659-99af-a7de06feb847',
        'funcx_endpoint_compute'     : '4c676cea-8382-4d5d-bc63-d6342bdb00ca'
    }

    # flow_input = {
    #     'input': {
    #         'staging_dir': '/eagle/APSDataAnalysis/XPCS_test/cooley_raf',
    #     }
    # }

class RyanProd(BaseDeployment):

    globus_endpoints = {
    'beamline_globus_ep' : 'c7e7f102-2166-11ec-8338-9d23a2dd9550',
    'eagle_globus_ep' : '05d2c76a-e867-4f67-aa57-76edeb0beda0',
    'theta_globus_ep': '08925f04-569f-11e7-bef8-22000b9a448b',
    'ssx_eagle_globus_ep' :'4340775f-4758-4fd6-a7b1-990f82aef5de'
    }

    funcx_endpoints = {
        'funcx_endpoint_non_compute' : '6c4323f4-a062-4551-a883-146a352a43f5',
        'funcx_endpoint_compute'     : '9f84f41e-dfb6-4633-97be-b46901e9384c'
    }



deployment_map = {
    'raf-prod': RafProd(),
    'ryan-prod': RyanProd(),
}
