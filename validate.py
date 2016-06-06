import timeit

import requests


def authenticate():
    body = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "name": "admin",
                        "password": "password",
			"domain": {
			    "id": "default"
			}
                    }
                }
            },
            "scope": {
                "project": {
                    "name": "admin",
		    "domain": {
                        "id": "default"
		    }
                }
            }
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://localhost:35357/v3/auth/tokens',
		             json=body,
			     headers=headers)
    assert response.status_code == 201
    token = response.headers.get('X-Subject-Token')
    print token
    return token


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
