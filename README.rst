OSIC Performance Bot
====================

Tools and scripts to assist in the automation of performance testing keystone
in review.

This repository contains a set of ansible scripts to help deploy a stand-alone
keystone service backed by MySQL using `OpenStack Ansible's Keystone Role
<https://github.com/openstack/openstack-ansible-os_keystone>`_. The plays and
variables defined here are minimal, assuming many of the defaults defined by
the the OpenStack Ansible project.

The following diagram illustrates the performance automation flow:

.. https://www.websequencediagrams.com/ source:
    title OSIC Performance Bot
    OpenStack Gerrit (review.openstack.org) -> Event Listener (listen.py): gerrit event stream
    Event Listener (listen.py) -> Event Scheduler (schedule.py): add patch metadata to queue
    Event Scheduler (schedule.py) -> Bare Metal Performance Host: create a new LXD Ubuntu 16.04 container
    Bare Metal Performance Host -> Ubuntu Container: ansible orchestration (keystone install)
    Event Scheduler (schedule.py) -> Bare Metal Performance Host: benchmark keystone master branch
    Bare Metal Performance Host -> Ubuntu Container: benchmark keystone master branch
    Ubuntu Container -> Bare Metal Performance Host: benchmark results
    Bare Metal Performance Host -> Event Scheduler (schedule.py): benchmark results
    Event Scheduler (schedule.py) -> Bare Metal Performance Host: benchmark patch from Gerrit
    Bare Metal Performance Host -> Ubuntu Container: benchmark patch from Gerrit
    Bare Metal Performance Host -> Event Scheduler (schedule.py): benchmark results
    Event Scheduler (schedule.py) -> OpenStack Gerrit (review.openstack.org): leave results as a comment on review
    Event Scheduler (schedule.py) -> Event Scheduler (schedule.py): remove patch metadata from queue

steps
-----

installing keystone
~~~~~~~~~~~~~~~~~~~

To install keystone and its dependencies, run the following::

    bash run_everything.sh

running basic performance tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This repository conatins a script to perform basic benchmark tests using
ApacheBench::

    $ bash benchmark.sh

The script will save the output from ApacheBench in four files named
``create_token`` and ``validate_token``. All files will be located in the
``results/`` directory.

The script assume a user has already been created by the ``os_keystone`` role.
