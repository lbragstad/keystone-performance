keystone-performance
====================
Tools and scripts for performance testing keystone.

This repository contains a set of ansible scripts to help deploy a stand-alone
keystone service backed by MySQL using `OpenStack Ansible's Keystone Role
<https://github.com/openstack/openstack-ansible-os_keystone>`_. The plays and
variables defined here are minimal, meaning that a lot of defaults are assumed
from the OpenStack Ansible project.

This is currently only expected to run against Ubuntu distributions.

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
``create_token``, ``validate_token``, ``create_token_concurrent``, and
``validate_token_concurrent``. All files will be located in the ``results/``
directory.

The script assume a user has already been created by the ``os_keystone`` role.
