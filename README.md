# keystone-performance
Tools and scripts for performance testing keystone.

This repository contains a set of ansible scripts to help deploy a stand-alone
keystone service backed by MySQL using [OpenStack Ansible's os_keystone
role](https://github.com/openstack/openstack-ansible-os_keystone). The plays
and variables defined here are minimal, meaning that a lot of defaults are
assumed from the OpenStack Ansible project.

This is currently only expected to run against Ubuntu distributions.

## steps

### installing keystone

To install keystone and its dependencies, run the following:

  `bash run_everything.sh`

### running basic performance tests

This repository contains two scripts that test basic usage of keystone. The
scripts are intended to be run from the host that is running keystone.

```
$ python authenticate.py
$ python validate.py
```

The output from the scripts will be the total wall time to complete 1000
requests against keystone, as well as the estimated average time per request.

The scripts assume a user has already been created by the `os_keystone` role.

## todos

* Find a way to reinstall keystone with patches from Gerrit. This will make it
  so that we can performance test patches *before* they merge.
* Add setup logic to populate keystone with a bunch of project, users,
  endpoints, etc. The goal of this is to make the data in keystone similar to
  that of a real deployment.
* Break the deployment from the tests so that the deployment of a performance
  node can be done against something other than `localhost`.
