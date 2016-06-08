#!/bin/bash

set -e

apt-get update
apt-get install -y build-essential python-dev libffi-dev libssl-dev
curl /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py | python3
mkdir /etc/ansible
pip install -r requirements.txt
ansible-galaxy install --role-file=ansible-role-requirements.yml --force
ansible-playbook -i inventory_localhost --sudo setup_database.yml
ansible-playbook -i inventory_localhost --sudo setup_perf_host.yml
