import timeit

from keystoneclient.v3 import client


def authenticate():
    project_scoped = client.Client(
        username='admin',
        password='password',
        project_name='admin',
        auth_url='http://localhost:35357/v3')
    print('%s' % project_scoped.auth_token)
    assert response.status_code == 20


if __name__ == '__main__':
    iterations = 1000
    timer = timeit.Timer('authenticate()', 'from __main__ import authenticate')
    total_time = timer.timeit(number=iterations)
    print 'Authenticated %r times in %r seconds' % (iterations, total_time)
    print '%r seconds per authentication request.' % (total_time / iterations)
