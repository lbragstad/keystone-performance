OSIC Performance Bot
====================

Tools and scripts to assist in the automation of performance testing keystone
patches in review.

This repository contains a set of ansible scripts to help deploy a stand-alone
keystone service backed by MySQL using `OpenStack Ansible's Keystone Role
<https://github.com/openstack/openstack-ansible-os_keystone>`_. The plays and
variables included in this playbook are minimal, assuming many of the defaults
defined by the the OpenStack Ansible project.

What does it do?
----------------

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


How do I run performance on a patch in review?
----------------------------------------------


Keystone performance testing is strictly opt-in. The OSIC Performance Bot will
not vote on patches and it will not run performance tests against all patches
proposed to the ``openstack/keystone`` project. It simply provides a datapoint
for contributors to consider when reviewing changes. If a comment is left on an
``openstack/keystone`` review containing ``check performance`` in the message,
the bot will performance test the patch against master and leave a comment on
the review when it is finished. The comment will contain the results of the
performance run against master and the results of the performance run against
keystone built with the patch in review.

Can I use ``keystone-performance`` locally?
-------------------------------------------

You sure can, but the scripts in this repository do make some assumptions about
the test environment. The performance host used to test patches in review
currently tests on Ubuntu 16.04. As stated above, keystone is deployed
according to preferences defined by OpenStack Ansible.

Installing a performance node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install keystone and its dependencies, run the following::

    bash run_everything.sh

This will install required package dependencies and use OpenStack Ansible to
install keystone. The default inventory is coded to run against ``localhost``.
The idea models the ``DevStack`` perspective of throwing away the host after
the tests are finished. Once ansible is finished, the node is ready for
performance testing.

Running performance
~~~~~~~~~~~~~~~~~~~

Included is a script to help perform basic benchmark tests using ApacheBench::

    bash benchmark.sh

The script will save the output from ApacheBench in two files named
``results/create_token`` and ``results/validate_token``.

The script assumes all required data has been created by the ``os_keystone``
role.

Running performance against a patch up for review
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``checkout_change.yml`` play will pull a change from
``https://review.openstack.org/`` and install it into the python virtual
environment created by OpenStack Ansible. The only piece of information
``checkout_change.yml`` needs is the refspec of the change you wish to test. It
can be invoked as follows::

    ansible-playbook \
        --sudo \
        --inventory-file=inventory_localhost \
        --extra-vars "ref=refs/changes/48/298748/9" \
        checkout_change.yml

After checking out and installing the change locally, benchmarks can be rerun
using the ``benchmark.sh`` script.
