import os

import pytest

from jina import Client, Document, DocumentArray

from jcloud.flow import CloudFlow

from jcloud.helper import get_dict_list_key_path, get_condition_from_status

flows_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flows')
flow_file = 'base_flow.yml'
protocol = 'http'


def test_scale_flow():
    with CloudFlow(path=os.path.join(flows_dir, flow_file)) as flow:

        assert flow.endpoints != {}
        assert 'gateway' in flow.endpoints
        gateway = flow.endpoints['gateway']
        assert gateway.startswith(f'{protocol}s://')

        status = flow._loop.run_until_complete(flow.status)
        cnd = get_condition_from_status(status)

        assert cnd is not None
        ltt = cnd["lastTransitionTime"]

        da = Client(host=gateway).post(
            on='/',
            inputs=DocumentArray(Document(text=f'text-{i}') for i in range(50)),
        )
        assert len(da.texts) == 50

        # scale executor to 2 replicas
        flow._loop.run_until_complete(flow.scale(executor='executor0', replicas=2))

        assert flow.endpoints != {}
        assert 'gateway' in flow.endpoints
        gateway = flow.endpoints['gateway']
        assert gateway.startswith(f'{protocol}s://')

        status = flow._loop.run_until_complete(flow.status)
        cnd = get_condition_from_status(status)
        assert cnd is not None

        nltt = cnd["lastTransitionTime"]
        assert ltt < nltt

        da = Client(host=gateway).post(
            on='/',
            inputs=DocumentArray(Document(text=f'text-{i}') for i in range(50)),
        )
        assert len(da.texts) == 50

        assert status['spec']['executors'][0]['replicas'] == 2
