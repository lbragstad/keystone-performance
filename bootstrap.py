import random
import threading
import uuid

from keystoneclient import exceptions
from keystoneclient.v3 import client

keystone = client.Client(
    username='admin',
    password='password',
    project_name='admin',
    project_domain_id='default',
    user_domain_id='default',
    auth_url='http://localhost:35357/v3/')

# create some roles
for _ in xrange(50):
    keystone.roles.create(name=uuid.uuid4().hex)

# create some services and endpoints so we have a sizeable catalog
for _ in xrange(20):
    service = keystone.services.create(name=uuid.uuid4().hex,
                                           type=uuid.uuid4().hex)

    for interface in ['admin', 'public', 'internal']:
        keystone.endpoints.create(service=service,
                                  interface=interface,
                                  url='http://localhost/')

# create a bunch of enabled service providers
for _ in xrange(20):
    auth_url = 'http://%s/' % uuid.uuid4().hex
    sp_url = 'http://%s/' % uuid.uuid4().hex
    keystone.federation.service_providers.create(id=uuid.uuid4().hex,
                                                 auth_url=auth_url,
                                                 sp_url=sp_url,
                                                 enabled=True)


def create_projects():
    # create a pile of projects, each with ten users and role assignments
    for _ in xrange(10):
        role = random.choice(keystone.roles.list())
        project = keystone.projects.create(domain='default',
                                           name=uuid.uuid4().hex)

        for _ in xrange(10):
            user = keystone.users.create(domain='default',
                                         default_project=project.id,
                                         name=uuid.uuid4().hex,
                                         password='password')
        keystone.roles.grant(user=user, project=project, role=role)

for i in xrange(100):
    t = threading.Thread(target=create_projects)
    t.start()
