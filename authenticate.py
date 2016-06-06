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
    print response.headers.get('X-Subject-Token')


if __name__ == '__main__':
    iterations = 1000
    timer = timeit.Timer('authenticate()', 'from __main__ import authenticate')
    total_time = timer.timeit(number=iterations)
    print 'Authenticated %r times in %r seconds' % (iterations, total_time)
    print '%r seconds per authentication request.' % (total_time / iterations)
