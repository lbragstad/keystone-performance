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

This repository conatins a script to perform basic benchmark tests using
ApacheBench.

```
$ bash benchmark.sh
```

The script will save the output from ApacheBench in four files named
`create_token`, `validate_token`, `create_token_concurrent`, and
`validate_token_concurrent`. All files will be located in the `results/`
directory.

The script assume a user has already been created by the `os_keystone` role.

## todos

* Find a way to reinstall keystone with patches from Gerrit. This will make it
  so that we can performance test patches *before* they merge.
* Add setup logic to populate keystone with a bunch of project, users,
  endpoints, etc. The goal of this is to make the data in keystone similar to
  that of a real deployment.
* Break the deployment from the tests so that the deployment of a performance
  node can be done against something other than `localhost`.
