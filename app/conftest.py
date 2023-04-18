import os
import pytest

os.environ['TESTING'] = 'True'

@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client