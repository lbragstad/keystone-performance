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

.. image:: https://www.websequencediagrams.com/cgi-bin/cdraw?lz=dGl0bGUgT1NJQyBQZXJmb3JtYW5jZSBCb3QKR2Vycml0IC0-IExpc3RlbmVyOiBnAA4GZXZlbnQgc3RyZWFtCgAWCCAtPiBTY2hlZHVsZXI6IGFkZCBwYXRjaCBtZXRhZGF0YSB0byBxdWV1ZQoAHgktPgBqDUhvc3Q6IGNyZWF0ZSBhIG5ldyBjb250YWluZXIKABkQIC0-IEMAFgg6IGluc3RhbGwgYW5kIGNvbmZpZ3VyZSBrZXlzdG9uAGgLIABfFWJlbmNobWFyawApCQBEBQCBPAUAWiAAHx0AgRkJAFggcmVzdWx0cwCBUhUAgkwLAB8SAIFNDQCDLwY6IGNvbW1lbnQgb24gcmV2aWV3AIFzDgCDHQtyZW1vdmUAgyQHZnJvbQCDHgY&s=napkin

.. https://www.websequencediagrams.com/ source:
    title OSIC Performance Bot
    Gerrit -> Listener: gerrit event stream
    Listener -> Scheduler: add patch metadata to queue
    Scheduler-> Performance Host: create a new container
    Performance Host -> Container: install and configure keystone
    Scheduler -> Performance Host: benchmark keystone and patch
    Performance Host -> Container: benchmark keystone and patch
    Container -> Performance Host: benchmark results
    Performance Host -> Scheduler: benchmark results
    Scheduler -> Gerrit: comment on review
    Scheduler -> Scheduler: remove patch from queue

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
