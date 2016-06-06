#!/bin/bash

curl https://bootstrap.pypa.io/get-pip.py | sudo python
sudo apt-get update
sudo apt-get install build-essential python-dev libffi-dev libssl-dev
sudo mkdir /etc/ansible
sudo chown -R ubuntu:ubuntu /etc/ansible/
ansible-galaxy install --role-file=ansible-role-requirements.yml --force
ansible-playbook -i inventory_localhost --sudo setup_perf_host.yml
