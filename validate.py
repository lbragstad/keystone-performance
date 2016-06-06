import timeit

import requests

from keystoneclient.v3 import client


def authenticate():
    project_scoped = client.Client(
        username='admin',
        password='password',
        project_name='admin',
        auth_url='http://localhost:35357/v3')
    print project_scoped.auth_token
    return project_scoped.auth_token


def validate(token):
    response = requests.get(
        'http://localhost:35357/v3/auth/tokens',
        headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': token,
            'X-Subject-Token': token
        }
    )
    assert response.status_code == 200


if __name__ == '__main__':
    iterations = 1000
    setup = """\
from __main__ import authenticate
from __main__ import validate
token = authenticate()
"""
    timer = timeit.Timer('validate(token)', setup=setup)
    total_time = timer.timeit(number=iterations)
    print 'Validated token %r times in %r seconds' % (iterations, total_time)
    print '%r seconds per validation request.' % (total_time / iterations)
