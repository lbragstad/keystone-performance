import json

import requests


def authenticate():
    with open('auth.json', 'r') as f:
        body = json.loads(f.read())
    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://localhost:35357/v3/auth/tokens',
                             json=body,
                             headers=headers)
    assert response.status_code == 201
    print response.headers.get('X-Subject-Token')


if __name__ == '__main__':
    authenticate()
